openerp.web_custom = function(instance) {
var QWeb = openerp.web.qweb;
    _t = instance.web._t;


instance.web.form.One2ManyListView.include({
    do_delete: function (ids) {
        var confirm = window.confirm(_t("Do you really want to delete this record?"));
        if (confirm == true)
            {
                return this._super(ids);
            } 
    },
});

};

