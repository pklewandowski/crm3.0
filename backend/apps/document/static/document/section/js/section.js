function ColumnSlider(slider, handles, options) {
    this.slider = slider;
    this.maxColumn = 4;
    this.update = function createSlider(handles) {
        try {
            this.slider.noUiSlider.destroy();
        } catch (err) {

        }
        noUiSlider.create(this.slider, {
            start: handles,
            //      connect: [true, true, true, true, true],
            tooltips: false,
            margin: options.margin ? options.margin: 1,
            filter: 2,
            step: options.step ? options.step: 1,
            range: {
                'min': options.min ? options.min : [0],
                'max': options.max
            },
            format: wNumb({
                decimals: 0
            }),

            pips: { // Show a scale with the slider
                mode: 'steps',
                stepped: true,
                density: options.density ? options.density: 1
            }
        });

        this.slider.noUiSlider.on('change', function (values, handle) {

            /*
            if (this.options.start.length === 1 && values[handle] < 12) {
                this.set(12);
            }
            */

            if (values[handle] < 1) {
                this.set(1);
            }
        });
    };

    this.getColumns = function () {
        //return this.slider.noUiSlider.options.start;
        let c = this.slider.noUiSlider.get();
        if(Array.isArray(c)) {
            return c.map(function(e) {
                return parseInt(e);
            });
        }
        else return [parseInt(c)];
    };

    let setHandles = function (columns) {
        let div = parseInt(12 / columns);
        let c = div;
        let handles = [];
        for (let i = 0; i < columns; i++) {
            handles.push(c);
            c += div;
        }
        return handles;
    };

    this.addColumn = function () {
        let columns = this.getColumns().length + 1;
        if (columns > this.maxColumn) {
            swal('Osiągnięto maksymalną liczbę kolumn', '', 'warning');
            return;
        }
        this.update(setHandles(columns));
    };

    this.removeColumn = function () {

        let columns = this.getColumns().length - 1;
        if (columns < 1) {
            swal('Sekcja musi posiadać przynajmniej jedną kolumnę', '', 'warning');
            return;
        }
        this.update(setHandles(columns));
    };

    this.update(handles);
}

