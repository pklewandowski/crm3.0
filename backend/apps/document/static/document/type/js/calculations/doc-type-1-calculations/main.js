// import LoanValueProposal from './loan-value-proposal.js';


let securityType = $('input[name$="1_5ee705ded2504ff49856f736529ba03f"]');
let requestedAmount = $('input[name$="1_bc8ed3b4a06548c1a0adc38cfa25baae"]');
let maxLoanValueIINet = $('input[name$="1_4452d9ae5b4047a188d44e4cf57b99a7"]');
let maxLoanValueIVNet = $('input[name$="1_c2746c5a7d384b41bd6eef4f4aa420bc"]');

let maxLoanValueIIGross = $('input[name$="1_9fd0e82fe574444d8832fc0186e92195"]');
let maxLoanValueIVGross = $('input[name$="1_1380877d7fc14dbe9a43ae2d70e4270d"]');

let commissionII = $('input[name$="1_3331fd8606554eeea38197bcfab6a845"]');
let commissionIV = $('input[name$="1_a91d15fb72164bd8833aaad5c83bdd3e"]');

let ltvIINet = $('input[name$="1_c40de3c252444170a6661289da2851db"]');
let ltvIIGross = $('input[name$="1_536a8c3b2c734527a6283e78e96a1466"]');

let ltvIVNet = $('input[name$="1_7c0e5faf4fa24aeb81c47fb07a5c26bb"]');
let ltvIVGross = $('input[name$="1_72464e3d06ae45608a0644790981c1a4"]');

let securityFormChoosen = $('select[name$="1_c032458a6e4d4377870718a356044230"]');

let loanValue = $('input[name$="1_2d241cb0dd7d4482b1156015b064f691"]');
let loanInstallment = $('input[name$="1_be48f4f71c2f452c807b43ababe921bc"]');
let loanCommission = $('input[name$="1_cb42d402395f9d423aa5ec79c9af0e0d"]');
let loanPeriod = $('input[name$="1_2811ed77edc743bba947c4b9682f3ee3"]');

let loanValueProposal = {
    II: {
        III: $('input[name$="1_b0618ba527264770b70cc35ea1053f23_2"]'),
        II: $('input[name$="1_b0618ba527264770b70cc35ea1053f23_1"]'),
        I: $('input[name$="1_b0618ba527264770b70cc35ea1053f23"]'),
        A: maxLoanValueIIGross,
    },
    IV: {
        III: $('input[name$="1_4fd23d32bf484093ae2bc6a2e7973a8d_2"]'),
        II: $('input[name$="1_4fd23d32bf484093ae2bc6a2e7973a8d_1"]'),
        I: $('input[name$="1_4fd23d32bf484093ae2bc6a2e7973a8d"]'),
        A: maxLoanValueIVGross,
    },
};

let loanCommissionProposal = {
    II: {
        III: $('input[name$="1_5820c757fdd74d3a8def353ebddf68b5_2"]'),
        II: $('input[name$="1_5820c757fdd74d3a8def353ebddf68b5_1"]'),
        I: $('input[name$="1_5820c757fdd74d3a8def353ebddf68b5"]'),
        A: commissionII,
    },
    IV: {
        III: $('input[name$="1_58bf55f6da8049639ea73b68fd6ae652_2"]'),
        II: $('input[name$="1_58bf55f6da8049639ea73b68fd6ae652_1"]'),
        I: $('input[name$="1_58bf55f6da8049639ea73b68fd6ae652"]'),
        A: commissionIV,
    },
};

let loanInstallmentValue = {
    II: $('input[name$="1_a30112ce690a4f0090c9330b9696014c"]'),
    IV: $('input[name$="1_ca4367e02876472fa610d0363b93b089"]')
};

let loanPeriodValue = {
    II: $('input[name$="1_037d9e12c2b14088aaeda0df0026b4e2"]'),
    IV: $('input[name$="1_98e626527fcc494998811cff1b0a0148"]')
};


//    wartosc zabezpieczenia
function calcMaxQuota(el, force) {
    "use strict";

    let container = el.closest(".document-section-row-body");
    let securityValueVal;
    if (securityType.val() === 'LAND') {
        securityValueVal = container.find($('input[name$="1_7178c0205923440bbe79abd25310c522"]')).val();
    } else {
        securityValueVal = container.find($('input[name$="1_48bf4cf225e54b178b1090c784e5353d"]')).val();
    }

    let ltvII = container.find($('input[name$="1_63dae1bf3f254b71829b8871ba75a3bf"]')).val();
    let ltvIV = container.find($('input[name$="1_ff0ca5ba74bd4566ab2b2dca347767d4"]')).val();

    let maxQuotaII = container.find($('input[name$="1_8ab449d24ebd498c92f742630a318a74"]'));
    let maxQuotaIV = container.find($('input[name$="1_71c8268f25bc402aaf9e202a1e9e49e2"]'));


    let validate = function () {
        return (isNumber(securityValueVal) && (isNumber(ltvII) || isNumber(ltvIV)));
    };
    let fn = function () {
        if (validate()) {
            if (isNumber(ltvII)) {
                maxQuotaII.val((securityValueVal * (ltvII / 100)).toFixed(2));
            } else {
                maxQuotaII.val(null);
            }
            if (isNumber(ltvIV)) {
                maxQuotaIV.val((securityValueVal * (ltvIV / 100)).toFixed(2));
            } else {
                maxQuotaIV.val(null);
            }
        } else {
            maxQuotaII.val(null);
            maxQuotaIV.val(null);
        }
        maxQuotaII.trigger('change');
        maxQuotaIV.trigger('change');
    };

    if (!force) {
        if (validate()) {
            swal({
                title: 'Czy przeliczyć max. kwotowanie?',
                type: 'warning',
                showCancelButton: true,
                confirmButtonText: "Tak, przelicz!",
                cancelButtonText: "Nie"
            }).then((result) => {
                if (result.value) {
                    fn();
                }
            });
        }
    } else {
        fn();
    }
}

function calcSecurityValue(el) {
    "use strict";
    let container = el.closest(".document-section-row-body");
    let priceMkw = container.find($('input[name$="1_f72e7ea08d9e492c9c78d388d9b7b959"]')).val();
    let mkw = container.find($('input[name$="1_525dcdd9a7d34c21afa1ee610bb8fa05"]')).val();
    let securityValue = container.find($('input[name$="1_48bf4cf225e54b178b1090c784e5353d"]'));
    if (isNumber(priceMkw) && isNumber(mkw)) {

        swal({
            title: 'Czy przeliczyć wartość zabezpieczenia?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonText: "Tak, przelicz!",
            cancelButtonText: "Nie"
        }).then((result) => {
            if (result.value) {
                securityValue.val((priceMkw * mkw).toFixed(2)).trigger('change');
            }
        });
    }
}

function _getSumMaxQuota(section) {
    "use strict";
    let val = 0;
    let q = 0;
    $("#attr_formset_35_tab_content").find(".document-section-row-body").each(function () {
        if (section === 2) {
            q = $(this).find('input[name$="1_8ab449d24ebd498c92f742630a318a74"]');

        } else if (section === 4) {
            q = $(this).find('input[name$="1_71c8268f25bc402aaf9e202a1e9e49e2"]');
        } else {
            return 0;
        }

        if (!q) {
            return true;
        }

        if (!isNumber(q.val())) {
            return true;
        }
        val += parseFloat(q.val());
    });

    return val;
}

function _getTotalSecurityAmount() {
    "use strict";
    let val = 0.0;
    $('input[name$="1_48bf4cf225e54b178b1090c784e5353d"]').each(function () {
        if (isNumber($(this).val())) {
            val += parseFloat($(this).val());
        }
    });
    return val;
}

function calcMaxLoanAmountNet() {
    "use strict";
    let sumMaxQuotaII = _getSumMaxQuota(2);
    let sumMaxQuotaIV = _getSumMaxQuota(4);
    let maxLoanValueII = 0;
    let maxLoanValueIV = 0;
    if (isNumber(requestedAmount.val())) {
        if (isNumber(sumMaxQuotaII)) {
            maxLoanValueII = Math.min(requestedAmount.val(), sumMaxQuotaII)
        }
        if (isNumber(sumMaxQuotaIV)) {
            maxLoanValueIV = Math.min(requestedAmount.val(), sumMaxQuotaIV)
        }
    }

    maxLoanValueIINet.val(maxLoanValueII.toFixed(2));
    maxLoanValueIVNet.val(maxLoanValueIV.toFixed(2));

    maxLoanValueIINet.trigger('change');
    maxLoanValueIVNet.trigger('change');

}

function calcMaxLoanAmountGross() {
    "use strict";
    if (isNumber(commissionII.val()) && isNumber(maxLoanValueIINet.val())) {
        maxLoanValueIIGross.val(((1 + commissionII.val() / 100) * maxLoanValueIINet.val()).toFixed(2));
    } else {
        maxLoanValueIIGross.val(null);
    }
    if (isNumber(commissionIV.val()) && isNumber(maxLoanValueIVNet.val())) {
        maxLoanValueIVGross.val(((1 + commissionIV.val() / 100) * maxLoanValueIVNet.val()).toFixed(2));

    } else {
        maxLoanValueIVGross.val(null);
    }
    maxLoanValueIIGross.trigger('change');
    maxLoanValueIVGross.trigger('change');
}

function calcLtvNet() {
    "use strict";
    let totalSecurityAmount = _getTotalSecurityAmount();

    if (totalSecurityAmount === 0) {
        ltvIINet.val(null);
        ltvIVNet.val(null);
    } else {
        if (isNumber(maxLoanValueIINet.val())) {
            ltvIINet.val(parseFloat(maxLoanValueIINet.val()) / totalSecurityAmount)
        } else {
            ltvIINet.val(null);
        }

        if (isNumber(maxLoanValueIVNet.val())) {
            ltvIVNet.val(parseFloat(maxLoanValueIVNet.val()) / totalSecurityAmount)
        } else {
            ltvIVNet.val(null);
        }
    }

    ltvIINet.val((ltvIINet.val() * 100).toFixed(2)).trigger('change');
    ltvIVNet.val((ltvIVNet.val() * 100).toFixed(2)).trigger('change');
}

function calcLtvGross() {
    "use strict";
    let totalSecurityAmount = _getTotalSecurityAmount();

    if (totalSecurityAmount === 0) {
        ltvIIGross.val(null);
        ltvIVGross.val(null);
    } else {

        if (isNumber(maxLoanValueIIGross.val())) {
            ltvIIGross.val(parseFloat(maxLoanValueIIGross.val()) / totalSecurityAmount)
        } else {
            ltvIIGross.val(null);
        }

        if (isNumber(maxLoanValueIVGross.val())) {
            ltvIVGross.val(parseFloat(maxLoanValueIVGross.val()) / totalSecurityAmount)
        } else {
            ltvIVGross.val(null);
        }
    }
    if (isNumber(ltvIIGross.val())) {
        ltvIIGross.val((ltvIIGross.val() * 100).toFixed(2)).trigger('change');
    }
    if (isNumber(ltvIVGross.val())) {
        ltvIVGross.val((ltvIVGross.val() * 100).toFixed(2)).trigger('change');
    }
}

$(document).ready(function () {
    // let lvp = new LoanValueProposal();

    /*
    Obliczenie wartości zabezpieczenia po zmianie na polach:
    - Powierzchnia mieszkalna (m.kw.)
    - Cena za m.kw.
    */
    $(document).on('change',
        'input[name$="1_f72e7ea08d9e492c9c78d388d9b7b959"], ' +
        'input[name$="1_525dcdd9a7d34c21afa1ee610bb8fa05"]', function () {
            "use strict";
            calcSecurityValue($(this));
        });


    let instalmentII = $('input[name$="1_a30112ce690a4f0090c9330b9696014c"]');
    let instalmentIV = $('input[name$="1_ca4367e02876472fa610d0363b93b089"]');


    $(document).on('change', 'input[name$="1_9fd0e82fe574444d8832fc0186e92195"]', function () {
        if (isNumber($(this).val())) {
            instalmentII.val(parseFloat($(this).val()) / 100);
        }
    });
    $(document).on('change', 'input[name$="1_1380877d7fc14dbe9a43ae2d70e4270d"]', function () {
        if (isNumber($(this).val())) {
            instalmentIV.val(parseFloat($(this).val()) / 100);
        }
    });

    $(document).on('change',
        'input[name$="1_63dae1bf3f254b71829b8871ba75a3bf"], ' +
        'input[name$="1_ff0ca5ba74bd4566ab2b2dca347767d4"], ' +
        'input[name$="1_48bf4cf225e54b178b1090c784e5353d"]', function () {
            calcMaxQuota($(this), true);
        });

    $(document).on('change',
        'input[name$="1_bc8ed3b4a06548c1a0adc38cfa25baae"], ' +
        'input[name$="1_8ab449d24ebd498c92f742630a318a74"], ' +
        'input[name$="1_71c8268f25bc402aaf9e202a1e9e49e2"]', function () {
            calcMaxLoanAmountNet();
        });

    $(`#${maxLoanValueIINet.attr('id')}, 
        #${maxLoanValueIVNet.attr('id')}, 
        #${commissionII.attr('id')}, 
        #${commissionIV.attr('id')}`).on('change', function () {
        calcMaxLoanAmountGross();
        calcLtvNet();
        // lvp.calcLoanValueProposals(maxLoanValueIINet.val(), maxLoanValueIVNet.val(), commissionII.val(), commissionIV.val())
    });

    $(`#${maxLoanValueIIGross.attr('id')}, 
   #${maxLoanValueIVGross.attr('id')}`).change(function () {
        calcLtvGross();
    });

    securityFormChoosen.change(function () {
        if (!$(this).val()) {
            loanValue.val(null);
            loanInstallment.val(null);
            loanCommission.val(null);
            return;
        }
        let lvp = loanValueProposal[$(this).val()];
        let lcp = loanCommissionProposal[$(this).val()];

        loanValue.val(lvp.III.val() ? lvp.III.val() :
            (lvp.II.val() ? lvp.II.val() :
                    (lvp.I.val() ? lvp.I.val() : lvp.A.val())
            )
        );

        let loanCommissionPrc = (lcp.III.val() ? lcp.III.val() :
                (lcp.II.val() ? lcp.II.val() :
                        (lcp.I.val() ? lcp.I.val() : lcp.A.val())
                )
        );

        if (isNumber(loanValue.val()) && isNumber(loanCommissionPrc)) {
            loanCommission.val((parseFloat(loanValue.val()) - (parseFloat(loanValue.val()) / (1 + parseFloat(loanCommissionPrc) / 100))).toFixed(2));
        }
        else {
            loanCommission.val(null);
        }

        loanInstallment.val(loanInstallmentValue[$(this).val()].val());
        loanPeriod.val(loanPeriodValue[$(this).val()].val());
    });
});
