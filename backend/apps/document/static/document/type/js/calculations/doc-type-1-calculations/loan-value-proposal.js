let LoanValueProposal = function() {

    this.securityOfficerProposal = {
        II: {
            value: $('input[name$="1_b0618ba527264770b70cc35ea1053f23"]'),
            comission: $('input[name$="1_5820c757fdd74d3a8def353ebddf68b5"]')
        },
        IV: {
            value: $('input[name$="1_4fd23d32bf484093ae2bc6a2e7973a8d"]'),
            comission: $('input[name$="1_58bf55f6da8049639ea73b68fd6ae652"]')
        }
    };

    this.managingOfficerProposal = {
        II: {
            value: $('input[name$="1_b0618ba527264770b70cc35ea1053f23_1"]'),
            comission: $('input[name$="1_5820c757fdd74d3a8def353ebddf68b5_1"]')
        },
        IV: {
            value: $('input[name$="1_4fd23d32bf484093ae2bc6a2e7973a8d_1"]'),
            comission: $('input[name$="1_58bf55f6da8049639ea73b68fd6ae652_1"]')
        }
    };

    this.generalOfficerProposal = {
        II: {
            value: $('input[name$="1_b0618ba527264770b70cc35ea1053f23_2"]'),
            comission: $('input[name$="1_5820c757fdd74d3a8def353ebddf68b5_2"]')
        },
        IV: {
            value: $('input[name$="1_4fd23d32bf484093ae2bc6a2e7973a8d_2"]'),
            comission: $('input[name$="1_58bf55f6da8049639ea73b68fd6ae652_2"]')
        }
    };

    this.securityOfficerProposal.II.value.change(() =>{
        if(isNumber(this.securityOfficerProposal.II.value.val())) {
            this.managingOfficerProposal.II.value.val(this.securityOfficerProposal.II.value.val())
        }
    });
    this.securityOfficerProposal.II.comission.change(() =>{
        if(isNumber(this.securityOfficerProposal.II.comission.val())) {
            this.managingOfficerProposal.II.comission.val(this.securityOfficerProposal.II.comission.val())
        }
    });

    this.securityOfficerProposal.IV.value.change(() =>{
        if(isNumber(this.securityOfficerProposal.IV.value.val())) {
            this.managingOfficerProposal.IV.value.val(this.securityOfficerProposal.IV.value.val())
        }
    });
    this.securityOfficerProposal.IV.comission.change(() =>{
        if(isNumber(this.securityOfficerProposal.IV.comission.val())) {
            this.managingOfficerProposal.IV.comission.val(this.securityOfficerProposal.IV.comission.val())
        }
    });


    this.managingOfficerProposal.II.value.change(() =>{
        if(isNumber(this.managingOfficerProposal.II.value.val())) {
            this.generalOfficerProposal.II.value.val(this.managingOfficerProposal.II.value.val())
        }
    });
    this.managingOfficerProposal.II.comission.change(() =>{
        if(isNumber(this.managingOfficerProposal.II.comission.val())) {
            this.generalOfficerProposal.II.comission.val(this.managingOfficerProposal.II.comission.val())
        }
    });

    this.managingOfficerProposal.IV.value.change(() =>{
        if(isNumber(this.managingOfficerProposal.IV.value.val())) {
            this.generalOfficerProposal.IV.value.val(this.managingOfficerProposal.IV.value.val())
        }
    });
    this.managingOfficerProposal.IV.comission.change(() =>{
        if(isNumber(this.managingOfficerProposal.IV.comission.val())) {
            this.generalOfficerProposal.IV.comission.val(this.managingOfficerProposal.IV.comission.val())
        }
    });

    this.init = function () {
        "use strict";
    };

    this.calcLoanValueProposals = function (valueII, valueIV, commII, commIV) {
        "use strict";
        this.securityOfficerProposal.II.value.val(valueII);
        this.securityOfficerProposal.IV.value.val(valueIV);
        this.securityOfficerProposal.II.comission.val(commII);
        this.securityOfficerProposal.IV.comission.val(commIV);

        this.managingOfficerProposal.II.value.val(valueII);
        this.managingOfficerProposal.IV.value.val(valueIV);
        this.managingOfficerProposal.II.comission.val(commII);
        this.managingOfficerProposal.IV.comission.val(commIV);

        this.generalOfficerProposal.II.value.val(valueII);
        this.generalOfficerProposal.IV.value.val(valueIV);
        this.generalOfficerProposal.II.comission.val(commII);
        this.generalOfficerProposal.IV.comission.val(commIV);
    };

    this.init();
};

// export default LoanValueProposal;

