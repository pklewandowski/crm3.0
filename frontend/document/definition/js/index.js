import DocumentDefinition from "./document-definition";


$(document).ready(function () {
    window.documentDefinition = new DocumentDefinition('documentDefinitionContainer', _g.document.type);
});