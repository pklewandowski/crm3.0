import {Hierarchy} from "./hierarchy";

$(document).ready(function () {
  let hierarchy = new Hierarchy("hierarchyStructure", "hierarchyFormModal", "userListModal", _g.hierarchy.rootNode);
  hierarchy.render();
});