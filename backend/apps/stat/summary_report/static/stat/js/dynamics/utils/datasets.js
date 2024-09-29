// backgroundColor: [
//     'rgba(255, 99, 132, 0.2)',
//     'rgba(54, 162, 235, 0.2)',
//     'rgba(255, 206, 86, 0.2)',
//     'rgba(75, 192, 192, 0.2)',
//     'rgba(153, 102, 255, 0.2)',
//     'rgba(255, 159, 64, 0.2)'
// ],

// borderColor: [
//     'rgba(255, 99, 132, 1)',
//     'rgba(54, 162, 235, 1)',
//     'rgba(255, 206, 86, 1)',
//     'rgba(75, 192, 192, 1)',
//     'rgba(153, 102, 255, 1)',
//     'rgba(255, 159, 64, 1)'
// ],

function initialDatasets(label) {
    return {
        // 'labels': [],
        'NEW': {
            label: "Nowa",
            stack: '0',
            data: [],
            borderColor: 'rgba(128,128,128)',
            backgroundColor: 'rgba(42,96,165,0.73)',
            borderWidth: 0
        },
        'PRLG': {
            label: 'Prolongata',
            stack: '0',
            data: [],
            borderColor: 'rgba(128,128,128)',
            backgroundColor: 'rgb(170, 33, 18, .7)',
            borderWidth: 0,
        },
        'ANX': {
            label: 'Aneks',
            stack: '0',
            data: [],
            borderColor: 'rgba(128,128,128)',
            backgroundColor: 'rgba(34,133,84,0.76)',
            borderWidth: 0,
        },
        'UGD': {
            label: 'Ugoda',
            stack: '0',
            data: [],
            borderColor: 'rgba(128,128,128)',
            backgroundColor: 'rgba(104,33,144,0.7)',
            borderWidth: 0,
        },
        'XXX': {
            label: 'Nieokreślono we wniosku',
            stack: '0',
            data: [],
            borderColor: 'rgba(128,128,128)',
            backgroundColor: 'rgba(97,97,97,0.7)',
            borderWidth: 0,
        }
    };
}

export {initialDatasets}