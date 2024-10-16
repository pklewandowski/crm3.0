function scrollBox() {
    var body = $('body');

    body.on('mouseenter', '.scroll-box', function () {
        $(this).stop();
        var boxWidth = $(this).width();
        var textWidth = $('.scroll-text', $(this)).width();
        if (textWidth > boxWidth) {
            var animSpeed = textWidth * 15;
            $(this).animate({
                scrollLeft: (textWidth - boxWidth)
            }, animSpeed, function () {
                $(this).animate({
                    scrollLeft: 0
                }, animSpeed, function () {
                    $(this).trigger('mouseenter');
                });
            });
        }
    });

    body.on('mouseleave', '.scroll-box', function () {
        var animSpeed = $(this).scrollLeft() * 10;
        $(this).stop().animate({
            scrollLeft: 0
        }, animSpeed);
    });
}

/*

$(document).ready(function () {
	    $('.scroll-box').mouseenter(function () {
	        $(this).stop();
	        var boxWidth = $(this).width();
	        var textWidth = $('.scroll-text', $(this)).width();
	        if (textWidth > boxWidth) {
	            var animSpeed = textWidth * 10;
	            $(this).animate({
	                scrollLeft: (textWidth - boxWidth)
	            }, animSpeed, function () {
	                $(this).animate({
	                    scrollLeft: 0
	                }, animSpeed, function () {
	                    $(this).trigger('mouseenter');
	                });
	            });
	        }
	    }).mouseleave(function () {
	        var animSpeed = $(this).scrollLeft() * 10;
	        $(this).stop().animate({
	            scrollLeft: 0
	        }, animSpeed);
	    });

	});*/
