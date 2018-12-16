openerp.custom_exception = function(instance) {

var QWeb = instance.web.qweb,
    _t = instance.web._t;

instance.web.CrashManager = instance.web.Class.extend({
    init: function() {
        this.active = true;
    },

    rpc_error: function(error) {
        if (!this.active) {
            return;
        }
        // yes, exception handling is shitty
        if (error.code === 300 && error.data && error.data.type == "client_exception" && error.data.debug.match("SessionExpiredException")) {
            this.show_warning({type: "Session Expired", data: {
                fault_code: _t("Your OpenERP session expired. Please refresh the current web page.")
            }});
            return;
        }
        if (error.data.fault_code) {
            var split = ("" + error.data.fault_code).split('\n')[0].split(' -- ');
            if (split.length > 1) {
                error.type = split.shift();
                error.data.fault_code = error.data.fault_code.substr(error.type.length + 4);
            }
        }
        if (error.code === 200 && error.type) {
            this.show_warning(error);
        } else {
            this.show_error(error);
        }
    },
    show_warning: function(error) {
        if (!this.active) {
            return;
        }
        instance.web.dialog($('<div>' + QWeb.render('CrashManager.warning', {error: error}) + '</div>'), {
            title: "OpenERP " + _.str.capitalize(error.type),
            buttons: [
                {text: _t("Ok"), click: function() { $(this).dialog("close"); }}
            ]
        });
    },
    show_error: function(error) {
        if (!this.active) {
            return;
        }
                var buttons = {};
        buttons[_t("Ok")] = function() {
            $(this).dialog("close");
        };

        if (instance.session.debug){
            var dialog = new instance.web.Dialog(this, {
                title: "extraERP " + _.str.capitalize(error.type),
                width: '80%',
                height: '50%',
                min_width: '800px',
                min_height: '600px',
                buttons: buttons
            }).open();
            dialog.$el.html(QWeb.render('CrashManager.error', {session: instance.session, error: error}));
        }
       
       else{

        var dialog = new instance.web.Dialog(this, {
            title: "Problem " + _.str.capitalize(error.type),
            width: '300px',
            height: '130px',
            buttons: buttons
        }).open();
        dialog.$el.html(" يوجد خطأ ، الرجاء الاتصال بمسؤول النظام .");
       }
    },
    show_message: function(exception) {
        this.show_error({
            type: _t("Client Error"),
            message: exception,
            data: {debug: ""}
        });
    },
});

}