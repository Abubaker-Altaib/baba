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

instance.web.form.FieldBinaryFile.include({
    on_clear: function() {
        console.log('----------------------------------child onclear22222222222222')
        var confirm = window.confirm(_t("Do you really want to clear this file?"));
        if (confirm == true){
            this._super.apply(this, arguments);
            this.$el.find('input').eq(0).val('');
            this.set_filename('');
        }
    }
});


instance.web.UserMenu =  instance.web.Widget.extend({
    template: "NCTRUserMenu",
    init: function(parent) {
        this._super(parent);
        this.update_promise = $.Deferred().resolve();
    },
    start: function() {
        var self = this;
        this._super.apply(this, arguments);
        this.$el.on('click', '.oe_dropdown_menu li a[data-menu]', function(ev) {
            ev.preventDefault();
            var f = self['on_menu_' + $(this).data('menu')];
            if (f) {
                f($(this));
            }
        });
    },
    do_update: function () {
        var self = this;
        var fct = function() {
            var $avatar = self.$el.find('.oe_topbar_avatar');
            $avatar.attr('src', $avatar.data('default-src'));
            if (!self.session.uid)
                return;
            var func = new instance.web.Model("res.users").get_func("read");
            return self.alive(func(self.session.uid, ["name", "company_id"])).then(function(res) {
                var topbar_name = res.name;
                if(instance.session.debug)
                    topbar_name = _.str.sprintf("%s (%s)", topbar_name, instance.session.db);
                if(res.company_id[0] > 1)
                    topbar_name = _.str.sprintf("%s (%s)", topbar_name, res.company_id[1]);
                self.$el.find('.oe_topbar_name').text(topbar_name);
                if (!instance.session.debug) {
                    topbar_name = _.str.sprintf("%s (%s)", topbar_name, instance.session.db);
                }
                var avatar_src = self.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: self.session.uid});
                $avatar.attr('src', avatar_src);
            });
        };
        this.update_promise = this.update_promise.then(fct, fct);
    },
    on_menu_help: function() {
        var link;
        model = new instance.web.Model("user.menu")
        model.query(['link'])
        .filter([['name' , '=' , 'help']])
        .all()
        .then(function (record) {
            link = record[0].link
            if (link)
                window.open( [link], "_blank" , 'location=yes,height=600,width=700,scrollbars=yes,status=yes');
            else{
                var dialog = new instance.web.Dialog(this, {
                title: _t("User Manual"),
                width: '360px',
                height: '150px',
            }).open();
            dialog.$el.html(_t("sad to tell you that user manual not available yet :( <br> too sorry !"));
            }
        })
    },
    on_menu_logout: function() {
        this.trigger('user_logout');
    },
    on_menu_settings: function() {
        var self = this;
        if (!this.getParent().has_uncommitted_changes()) {
            self.rpc("/web/action/load", { action_id: "base.action_res_users_my" }).done(function(result) {
                result.res_id = instance.session.uid;
                self.getParent().action_manager.do_action(result);
            });
        }
    },
    on_menu_account: function() {
        var self = this;
        if (!this.getParent().has_uncommitted_changes()) {
            var P = new instance.web.Model('ir.config_parameter');
            P.call('get_param', ['database.uuid']).then(function(dbuuid) {
                var state = {
                            'd': instance.session.db,
                            'u': window.location.protocol + '//' + window.location.host,
                        };
                var params = {
                    response_type: 'token',
                    client_id: dbuuid || '',
                    state: JSON.stringify(state),
                    scope: 'userinfo',
                };
                instance.web.redirect('https://accounts.openerp.com/oauth2/auth?'+$.param(params));
            });
        }
    },

    on_menu_debug: function() {
        window.location = $.param.querystring( window.location.href, 'debug');
    },

    on_menu_reports: function() {
        var link;
        model = new instance.web.Model("user.menu")
        model.query(['link'])
        .filter([['name' , '=' , 'report']])
        .all()
        .then(function (record) {
            link = record[0].link
            if (link)
                window.open( [link], "_blank" , 'location=yes,height=600,width=700,scrollbars=yes,status=yes');
            else{
                var dialog = new instance.web.Dialog(this, {
                title: _t("Reports"),
                width: '360px',
                height: '150px',
            }).open();
            dialog.$el.html(_t("Report System Not Available yet :( <br> too sorry !"));
            }
        })
        
        //instance.web.redirect();
    },

    on_menu_about: function() {
        var self = this;
        self.rpc("/web/webclient/version_info", {}).done(function(res) {
            var $help = $(QWeb.render("NCTRUserMenu.about", {version_info: res}));
            $help.find('a.oe_activate_debug_mode').click(function (e) {
                e.preventDefault();
                window.location = $.param.querystring( window.location.href, 'debug');
            });
            instance.web.dialog($help, {autoOpen: true,
                modal: true, width: 507, height: 290, resizable: false, title: _t("About")});
        });
    },
});

};

