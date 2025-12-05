from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document
import lark_oapi as lark
from lark_oapi.api.docs.v1 import GetContentRequest
from lark_oapi.api.docx.v1 import GetDocumentRequest
from lark_oapi.api.wiki.v2 import (
    GetNodeSpaceRequest,
    GetSpaceRequest,
    ListSpaceNodeRequest,
)

from typing import Iterator

### TODO: Restructure the metadata to show the Lark Wiki/Docs hierarchy better.


class LarkSuiteDocLoader(BaseLoader):
    client: lark.Client
    document_id: str

    def __init__(self, client: lark.Client, document_id: str):
        self.client = client
        self.document_id = document_id

    def lazy_load(self) -> Iterator[Document]:
        request_metadata = (
            GetDocumentRequest.builder().document_id(self.document_id).build()
        )

        response_metadata = self.client.docx.v1.document.get(request_metadata)
        if not response_metadata.success():
            raise RuntimeError(
                f"Failed to fetch document metadata: {response_metadata.msg}"
            )

        metadata = {
            "document_id": self.document_id,
            "revision_id": response_metadata.data.document.revision_id,
            "title": response_metadata.data.document.title,
            "type": "lark-doc",
            "source": f"lark-doc://{self.document_id}",
        }

        request_content = (
            GetContentRequest.builder()
            .content_type("markdown")
            .doc_type("docx")
            .doc_token(self.document_id)
            .build()
        )

        response_content = self.client.docs.v1.content.get(request_content)
        if not response_content.success():
            raise RuntimeError(
                f"Failed to fetch document content: {response_content.msg}"
            )

        content = response_content.data.content

        if content is None:
            content = ""

        yield Document(page_content=str(content), metadata=metadata)


class LarkSuiteWikiLoader(LarkSuiteDocLoader):
    wiki_metadata: dict
    wiki_id: str

    def __init__(self, client: lark.Client, wiki_id: str):
        request = GetNodeSpaceRequest.builder().token(wiki_id).obj_type("wiki").build()

        response = client.wiki.v2.space.get_node(request)
        if not response.success():
            raise RuntimeError(f"Failed to fetch wiki node space: {response.msg}")

        self.wiki_id = wiki_id
        self.wiki_metadata = {
            "owner": response.data.node.owner,
            "creator": response.data.node.creator,
        }

        document_id = response.data.node.obj_token
        if not document_id:
            raise RuntimeError("Wiki node space does not contain a valid document ID.")
        super().__init__(client=client, document_id=str(document_id))

    def lazy_load(self) -> Iterator[Document]:
        document = super().lazy_load()
        for doc in document:
            doc.metadata["source"] = f"lark-wiki://{self.wiki_id}"
            doc.metadata["type"] = "lark-wiki"
            doc.metadata["lark_owner"] = self.wiki_metadata["owner"]
            doc.metadata["lark_creator"] = self.wiki_metadata["creator"]
            yield doc


class LarkSuiteWikiSpaceLoader(BaseLoader):
    client: lark.Client
    space_id: str
    space_name: str
    space_description: str

    def __init__(self, client: lark.Client, space_id: str):
        self.client = client
        self.space_id = space_id
        request = GetSpaceRequest.builder().space_id(self.space_id).build()

        response = self.client.wiki.v2.space.get(request)
        if not response.success():
            raise RuntimeError(f"Failed to fetch wiki node space: {response.msg}")

        self.space_name = (
            str(response.data.space.name) if response.data.space.name else ""
        )
        self.space_description = (
            str(response.data.space.description)
            if response.data.space.description
            else ""
        )

    def lazy_load(self) -> Iterator[Document]:
        yield from self.__lazy_load_space_node_children(space_id=self.space_id)

    def __lazy_load_space_node_children(
        self, space_id: str, parent_node_token: str = ""
    ) -> Iterator[Document]:
        ### TODO: handle pagination
        request = ListSpaceNodeRequest.builder().space_id(space_id).page_size(50)
        if parent_node_token != "":
            request.parent_node_token(parent_node_token)
        request = request.build()

        response = self.client.wiki.v2.space_node.list(request)
        if not response.success():
            raise RuntimeError(f"Failed to list wiki space nodes: {response.msg}")
        if not response.data.items:
            return

        for node in response.data.items:
            ### TODO: handle other obj_types
            node_token = node.node_token if node.node_token else ""
            if node.obj_type == "docx":
                loader = LarkSuiteWikiLoader(client=self.client, wiki_id=node_token)
                for doc in loader.lazy_load():
                    doc.metadata["source"] = f"lark-space://{self.space_id}"
                    doc.metadata["space_name"] = self.space_name
                    doc.metadata["space_description"] = self.space_description
                    yield doc
            if node.has_child:
                yield from self.__lazy_load_space_node_children(
                    space_id=space_id, parent_node_token=node_token
                )
        return
