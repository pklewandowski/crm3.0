(function ($) {

    var colors = ['rgb(243, 211, 141)', 'rgb(214, 241, 198)', 'rgb(210, 231, 249)'];

    $.fn.stickyNotes = function (mode, options) {

        var add = function (container, data) {

            var degs = Math.floor(Math.random() * 20) - 10;
            var cl = Math.floor(Math.random() * 3);

            var sticky = $('<div data-rotate="' + degs + '" class="sticky-note ' + 'sticky-rotate' + degs + '" style="background-color: ' + colors[cl] + ';"></div>');
            sticky.html('<div class="sticky-note-bar"><div style="float:right"><i class="fa fa-close"></i></div></div><div>' +
                '<input spellcheck="false" class="sticky-note-title" placeholder="Tytuł"/><textarea spellcheck="false" class="sticky-note-body"></textarea></div>');

            sticky.draggable({
                start: function (event, ui) {
                    $(this).addClass('sticky-note-drag');
                },
                stop: function (event, ui) {
                    $(this).removeClass('sticky-note-drag');
                }
            });

            sticky.css({"position": "absolute", 'left': '300px', 'top': '300px'}); // , 'transform':'rotate(' + degs + 'deg)'

            container.append(sticky);
        }

        var settings = $.extend({
            // These are the defaults.
            color: "#556b2f",
            backgroundColor: "white",
            data: []
        }, options)

        switch (mode) {

            case 'toggle':
                this.toggle();
                break;

            case 'add':
                add(this, null);
                break;

            default:
                break;
        }
    }

}(jQuery));
