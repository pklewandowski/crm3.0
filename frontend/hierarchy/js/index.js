import {Hierarchy} from "./hierarchy";

document.addEventListener("DOMContentLoaded", function() {
  let hierarchy = new Hierarchy("hierarchyStructure", "hierarchyFormModal", _g.hierarchy.rootNode);
  hierarchy.render();
});