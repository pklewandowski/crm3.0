function basicOCR() {

	Tesseract.recognize('Przechwytywanie.JPG', {
		lang: 'pol',
		tessedit_char_blacklist: 'e'
	})
	.then(function(result){
		console.log(result)
	});
}

function runOCR(url) {
    Tesseract.recognize(url, {lang:'pol'})
         .then(function(result) {
		    console.log(result);
            document.getElementById("ocr_results")
                    .innerText = result.text;
         }).progress(function(result) {
            document.getElementById("ocr_status")
                    .innerText = result["status"] + " (" +
                        Math.round(result["progress"] * 100) + "%)";
        });
}

$(document).ready(function(){

    $('#start-ocr-btn').click(function(){
        runOCR(imgUrl);
    });


});

//document.getElementById("go_button")
//        .addEventListener("click", function(e) {
//			//basicOCR();
//           // var url = document.getElementById("url").value;
//            runOCR(imgUrl);
//        });