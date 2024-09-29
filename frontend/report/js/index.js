//
//
// var pdfjsLib = require("pdfjs-dist");
//
// var pdfPath = "/media/reports/generated/df73a47654914c5ca4c14a7bcf8e3058.pdf";
//
// // Setting worker path to worker bundle.
// pdfjsLib.GlobalWorkerOptions.workerSrc =
//   "../../build/browserify/pdf.worker.bundle.js";
//
// // Loading a document.
// var loadingTask = pdfjsLib.getDocument(pdfPath);
// loadingTask.promise
//   .then(function (pdfDocument) {
//     // Request a first page
//     return pdfDocument.getPage(1).then(function (pdfPage) {
//       // Display page on the existing canvas with 100% scale.
//       var viewport = pdfPage.getViewport({ scale: 1.0 });
//       var canvas = document.getElementById("reportPreviewCanvas");
//       canvas.width = viewport.width;
//       canvas.height = viewport.height;
//       var ctx = canvas.getContext("2d");
//       var renderTask = pdfPage.render({
//         canvasContext: ctx,
//         viewport,
//       });
//       return renderTask.promise;
//     });
//   })
//   .catch(function (reason) {
//     console.error("Error: " + reason);
//   });


