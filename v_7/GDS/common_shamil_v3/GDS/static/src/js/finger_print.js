/*
 *    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
 *    All Rights Reserved.
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU Affero General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Affero General Public License for more details.
 *
 *   You should have received a copy of the GNU Affero General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
//var quality = 60; //(1 to 100) (recommanded minimum 55)
//var timeout = 10; // seconds (minimum=10(recommanded), maximum=60, unlimited=0 )

openerp.GDS = function(instance) {
    var _t = instance.web._t,
    _lt = instance.web._lt;
    var QWeb = instance.web.qweb;


    instance.bio_req = instance.web.Widget.extend({
 
    init: function(parent , action) {
        this.NitgenRequest = { "Quality": 60, "TimeOut": 10 }
        this._super(parent, action);
        this.finger = action.params.finger;
        this.FINGER_SUCCESS_PERCENT = 30.0
        //this.employee_id = action.params.employee_id;
    },

    create_img : function(img_name ,img_data){
        var data = {'img_data' : img_data}
        $.ajax({ 
            url: 'http://localhost:8082/bio/create/'+img_name,
            async:false,
            type:"POST",
            data: JSON.stringify(data),
            contentType: "application/json",
            success : function(result){
                console.log(result)
                console.log("created");
            },
        });
    },

    compare : function(){
       // var result = "";
       var res = false;
       $.ajax({ 
            url: 'http://localhost:8082/bio/mach',
            async:false,
            success : function(result){
                console.log(result)
                res =  result;
            }
        });

       return res;
    },


    capture_new : function(){
        self = this
        img_data = ""
        $.ajax({ 
            type:"POST",
            async:false,
            contentType: "application/json",
            url: 'http://localhost:9101/bioenable/capture',
            data: JSON.stringify(self.NitgenRequest),
            success : function(result){
                img_data = result['BitmapData']
                //self.create_img("new.png" , img_data)
            } , 
        });  
    },

  open_employee_view : function(ids){
      this.do_action({
            name: "Employee Form",
            type: "ir.actions.act_window",
            res_model: "hr.employee",
            domain : [['id' , 'in' , ids]],
            views: [[false, "kanban"],[false, "list"] ,[false, "form"]],
            target: 'current',
            context: {},
            view_type : 'kanban',
            view_mode : 'kanban'
        });  
    },


    start: function(){
        this.capture_new()
        var finger = this.finger;
        var self = this;
        mach_ids = []
        model = new instance.web.Model("hr.employee")
        model.query(['id', finger]).all()
        .then(function (employee) {
            for (var i = 0; i < 5 ; i++) {
                console.log("employee " + employee[i].id);
                //var img_data = model.call("read_img" , [employee[i].id , finger] , {} )
                self.create_img("ref.png" , employee[i][finger]);
                //self.create_img("new.png" , employee[i][finger]); 
                var r = self.compare();
                //var r = 30;
                if (parseFloat(r) >= self.FINGER_SUCCESS_PERCENT){
                    mach_ids.push(employee[i].id);
                    console.log("append it");
                }
            }//for end
                self.open_employee_view(mach_ids);
            });//then end
        
       
    },
});
   

instance.bio_auth = instance.web.Widget.extend({
 
    init: function(parent , action) {
        this.NitgenRequest = { "Quality": 60, "TimeOut": 10 }
        this._super(parent, action);
        this.finger = action.params.finger;
        this.state = action.params.state;
        this.payment_id = action.params.payment_id;
        this.employee_id = action.params.employee_id;
    },



    capture_new : function(){

        self = this
        img_data = ""
        $.ajax({ 
            type:"POST",
            async:false,
            contentType: "application/json",
            url: 'http://localhost:9101/bioenable/capture',
            data: JSON.stringify(self.NitgenRequest),
            success : function(result){
                img_data = result['BitmapData']
                //self.create_img("new.png" , img_data)
            } , 
        });  
        return img_data
    },


    start: function(){
        var finger = this.finger;
        var self = this;
        var data = this.capture_new()
        model = new instance.web.Model("hr.employee")
        var u = model.call("process_bio" , [self.employee_id , data, "new.png" ,finger ,self.payment_id , self.state] , {} );
        u.then(function (reponse) {
            //alert(reponse);
            if (reponse == 1){
                var dialog = new instance.web.Dialog(this, {
                    title: "نظام شامل " ,
                    width: '330px',
                    height: '130px',
                    buttons: [
                        {text: _t("Ok"), click: function() { $(this).dialog("close"); }}
                    ]
                    }).open();
                    dialog.$el.html("<center> البصمة غير مطابقة </center>");

                }   

            self.getParent().history_back();
            self.destroy();                 
            });                  
    },
});

   

   instance.web.form.FieldLocalImage = instance.web.form.FieldBinary.extend({
    template: 'FieldBinaryImage',
    placeholder: "/GDS/static/src/img/fingerPrint.png",
    render_value: function() {
        var self = this;
        var url;
        var id = JSON.stringify(this.view.datarecord.id || null);
        var field = this.name;

        if (id == "null"){
            var $img = $(QWeb.render("FieldBinaryImage-img", { widget: self, url: this.placeholder }));
            self.$el.find('> img').remove();
            self.$el.prepend($img);
            $img.load(function() {
                if (! self.options.size)
                    return;
            $img.css("max-width", "" + self.options.size[0] + "px");
            $img.css("max-height", "" + self.options.size[1] + "px");
            $img.css("margin-left", "" + (self.options.size[0] - $img.width()) / 2 + "px");
            $img.css("margin-top", "" + (self.options.size[1] - $img.height()) / 2 + "px");
            });
            return;
        }
        model = new instance.web.Model("hr.employee")
        model.query([field])
             .filter([['id', '=', id]])
             .all().then(function (employee) {
                for (var i = 0; i < employee.length; i++) {
                   url = employee[i][field]
                   console.log(url)

                   var $img = $(QWeb.render("FieldBinaryImage-img", { widget: self, url: url }));
                   self.$el.find('> img').remove();
                   self.$el.prepend($img);
                    $img.load(function() {
            if (! self.options.size)
                return;
            $img.css("max-width", "" + self.options.size[0] + "px");
            $img.css("max-height", "" + self.options.size[1] + "px");
            $img.css("margin-left", "" + (self.options.size[0] - $img.width()) / 2 + "px");
            $img.css("margin-top", "" + (self.options.size[1] - $img.height()) / 2 + "px");
        });
                    $img.on('error', function() {
            $img.attr('src', self.placeholder);
            //instance.webclient.notification.warn(_t("Image"), _t("Could not display the selected image."));
        });
                }                
        });
    },
    on_file_uploaded_and_valid: function(size, name, content_type, file_base64) {
        this.internal_set_value(file_base64);
        this.binary_value = true;
        this.render_value();
        this.set_filename(name);
    },
    on_clear: function() {
        this._super.apply(this, arguments);
        this.render_value();
        this.set_filename('');
    }
});

   instance.web.form.LocalEmployeeImage = instance.web.form.FieldBinary.extend({
    template: 'FieldBinaryImage',
    placeholder: "/GDS/static/src/img/av.png",
    render_value: function() {
        var self = this;
        var url;
        var id = JSON.stringify(this.view.datarecord.id || null);
        var field = this.name;
        if (id == "null"){
            var $img = $(QWeb.render("FieldBinaryImage-img", { widget: self, url: this.placeholder }));
            self.$el.find('> img').remove();
            self.$el.prepend($img);
            $img.load(function() {
                if (! self.options.size)
                    return;
            $img.css("max-width", "" + self.options.size[0] + "px");
            $img.css("max-height", "" + self.options.size[1] + "px");
            $img.css("margin-left", "" + (self.options.size[0] - $img.width()) / 2 + "px");
            $img.css("margin-top", "" + (self.options.size[1] - $img.height()) / 2 + "px");
            });
            return;
        }
        model = new instance.web.Model("hr.employee")
        model.query([field])
             .filter([['id', '=', id]])
             .all().then(function (employee) {
                for (var i = 0; i < employee.length; i++) {
                   url = employee[i][field]
                   console.log(url)

                   var $img = $(QWeb.render("FieldBinaryImage-img", { widget: self, url: url }));
                   self.$el.find('> img').remove();
                   self.$el.prepend($img);
                    $img.load(function() {
            if (! self.options.size)
                return;
            $img.css("max-width", "180px");
            $img.css("max-height", "180px");
            $img.css("margin-left", "" + (self.options.size[0] - $img.width()) / 2 + "px");
            $img.css("margin-top", "" + (self.options.size[1] - $img.height()) / 2 + "px");
        });
                    $img.on('error', function() {
            $img.attr('src', self.placeholder);
            //instance.webclient.notification.warn(_t("Image"), _t("Could not display the selected image."));
        });
                }                
        });
    },
    on_file_uploaded_and_valid: function(size, name, content_type, file_base64) {
        this.internal_set_value(file_base64);
        this.binary_value = true;
        this.render_value();
        this.set_filename(name);
    },
    on_clear: function() {
        this._super.apply(this, arguments);
        this.render_value();
        this.set_filename('');
    }
});


   instance.finger_print_store_wedgit = instance.web.Widget.extend({
 
    init: function(parent , action) {
            this._super(parent, action);
            this.finger = action.params.finger;
            this.employee_id = action.params.employee_id;
        },
    start: function(){
        var NitgenRequest = {
          "Quality": 60,
          "TimeOut": 10
           }

        var finger = this.finger;
        var employee_id = this.employee_id
        var self = this;
           $.ajax({ 
                type:"POST",
                contentType: "application/json",
                url: 'http://localhost:9101/bioenable/capture',
                data: JSON.stringify(NitgenRequest),
                success : function(result){
                    data = result['BitmapData']
                    vals = {};
                    vals[finger] = data
                    var img_name = employee_id+"_"+self.finger+".png"
                    model = new instance.web.Model("hr.employee")
                    model.call("create_img" ,[ employee_id ,data ,self.finger ]).then(function(response){
                        if(! response)
                            alert('عذرا يوجد بصمة مشابهة')
                        self.getParent().history_back();
                        self.destroy();
                    });//call python method for create image in module files
                    //model.call('write', [employee_id, vals]).then(null);                    
                    
                } , 


            });    
    },
});

    instance.payment_recieve = instance.web.Widget.extend({
 
        init: function(parent , action) {
            this._super(parent, action);
            this.payment_receive_id = action.params.payment_receive_id;
            this.employee_id = action.params.employee_id;
            this.finger = action.params.finger
            this.state = action.params.state;
            this.bio_auth = new instance.bio_auth(parent, action)
            },

        start :function(){

            this.auth_start();
            
        
        },

        auth_start: function(){
            var finger = this.finger;
            var self = this;
            var data = this.bio_auth.capture_new()
            model = new instance.web.Model("hr.employee")
            var u = model.call("process_bio" , [self.employee_id , data, "new.png" ,finger ,self.payment_receive_id , self.state , "payment.receive"] , {} );
            u.then(function (reponse) {
                //alert(reponse);
                if (reponse == 1){
                    var dialog = new instance.web.Dialog(this, {
                        title: "نظام شامل " ,
                        width: '330px',
                        height: '130px',
                        buttons: [
                            {text: _t("Ok"), click: function() { $(this).dialog("close"); }}
                        ]
                        }).open();
                        dialog.$el.html('<center><h2 style="color:red"> البصمة غير مطابقة </h2></center>');

                    } 

                else if (reponse == 0){
                    self.employee_image()
                } 
                self.getParent().history_back();
                self.destroy();                
                });                  
        },

        success_dialog : function(url){
            html = '<center><img src="'+url+'"/><br /><h2 style="color:green">البصمة مطابقة</h2></center>'
            var dialog = new instance.web.Dialog(this, {
                    title: "نظام شامل " ,
                    //width: '330px',
                    //height: '130px',
                    buttons: [
                        {text: _t("Ok"), click: function() { $(this).dialog("close"); }}
                    ]
                    }).open();
                    dialog.$el.html(html);
                    
        },

        employee_image : function(){
            self = this;
            url = 'data:image/png;base64,'
            employee_id = this.employee_id
            model = new instance.web.Model("hr.employee")
            model.query(['image'])
             .filter([['id', '=', employee_id]])
             .all().then(function (employee) {
                url += employee[0]['image']
                self.success_dialog(url);
             });

            return url
        },

    });

    instance.fingerprint_search = instance.web.Widget.extend({
        init: function(parent , action) {
            this.NitgenRequest = { "Quality": 60, "TimeOut": 10 }
            this._super(parent, action);
            this.finger = action.params.finger;
            this.FINGER_SUCCESS_PERCENT = 30.0
            //this.employee_id = action.params.employee_id;
        },

        capture_new : function(){
        self = this
        img_data = ""
        $.ajax({ 
            type:"POST",
            async:false,
            contentType: "application/json",
            url: 'http://localhost:9101/bioenable/capture',
            data: JSON.stringify(self.NitgenRequest),
            success : function(result){
                img_data = result['BitmapData']
                //self.create_img("new.png" , img_data)
            } , 
        });  

        return img_data;
    },

     open_employee_view : function(ids){
          this.do_action({
                name: "Employee Form",
                type: "ir.actions.act_window",
                res_model: "hr.employee",
                domain : [['id' , 'in' , ids]],
                views: [[false, "kanban"],[false, "list"] ,[false, "form"]],
                target: 'current',
                context: {},
                view_type : 'kanban',
                view_mode : 'kanban'
            });  
        },

        start : function(){
            img_data = this.capture_new();
            model = new instance.web.Model("finger.print")
            self = this
            model.call("fingerprint_search" ,[img_data ,self.finger ]).then(function(result){
                if (result)
                    self.open_employee_view(result)

                else{
                     alert('لم يتم العثور')
                    //self.getParent().history_back();
                    self.destroy();
                }
                model.call("clean" , ['*.xyt' , '*.brw' , '*.dm' , '*.hcm' , '*.lcm' ,'*.lfm' , '*.qm' ,'*.min'])

            });
        }

    });

   instance.web.client_actions.add("payment_recieve", "instance.payment_recieve");
   instance.web.client_actions.add("finger_auth", "instance.bio_auth");
   instance.web.client_actions.add("finger_print_store", "instance.finger_print_store_wedgit");
   //instance.web.client_actions.add("bio_request", "instance.bio_req");
   instance.web.client_actions.add("bio_request", "instance.fingerprint_search");  
   instance.web.form.widgets.add("employee_image" , "instance.web.form.LocalEmployeeImage");
   instance.web.form.widgets.add("local_image" , "instance.web.form.FieldLocalImage");
};
