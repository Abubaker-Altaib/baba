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

openerp.image_attach = function(instance) {
    var _t = instance.web._t,
    _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

 instance.web.form.LocalEmployeeImage = instance.web.form.FieldBinary.extend({
    template: 'FieldBinaryImage',
    placeholder: "/image_attach/static/src/img/av.png",
    
    render_value: function(img_path="null") {
        var self = this;
        var url;
        var id = JSON.stringify(this.view.datarecord.id || null);
        var field = this.name;
        if (img_path=="null"){
           img_path= "/image_attach/static/src/img/av.png";
           }
        if (id == "null"){
            //console.log(this.placeholder)
            console.log("img path")
            console.log(img_path)
            var $img = $(QWeb.render("FieldBinaryImage-img", { widget: self, url: img_path }));
            self.$el.find('> img').remove();
            self.$el.prepend($img);
            $img.load(function() {
                //console.log("3")
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
                   //console.log("4")

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
        //console.log(file_base64)
        var NitgenRequest = {
          "Quality": 60,
          "TimeOut": 10
           }
        //console.log("beforeimg")
        var employee_id =JSON.stringify(this.view.datarecord.id || null);
        var self = this;
        //console.log("afterimg")
           $.ajax({
                type:"POST",
                contentType: "application/json",
                //url: 'http://localhost:9101/bioenable/capture',
                //data: JSON.stringify(NitgenRequest),
                success : function(result){
                    data = file_base64
                    vals = {};
                    //console.log("5")
                    //var img_name = employee_id+"_"+self.finger+".png"
                    //model = new instance.web.Model("hr.employee")
                    model.call("set_image_local" ,[ employee_id ,data]).then(function(response){
                        //console.log("RE")
                        //console.log(response)
                        if(! response)
                            alert('عذرا لا يوجد صورة')
                        //self.getParent().history_back();
                        var img_path=response
                        self.render_value(img_path)
                        //self.destroy();
                    });//call python method for create image in module files
                    //model.call('write', [employee_id, vals]).then(null);

                } ,


            });
    },
    on_clear: function() {
        this._super.apply(this, arguments);
        this.render_value();
        this.set_filename('');
    },
    on_file_uploaded: function(size, name, content_type, file_base64) {
        if (size === false) {
            this.do_warn(_t("File Upload"), _t("There was a problem while uploading your file"));
            // TODO: use openerp web crashmanager
            console.warn("Error while uploading file : ", name);
        } else {
            this.filename = name;
            this.on_file_uploaded_and_valid.apply(this, arguments);
        }
        this.$el.find('.oe_form_binary_progress').hide();
        this.$el.find('.oe_form_binary').show();
    }
});




 
   instance.web.form.widgets.add("employee_image" , "instance.web.form.LocalEmployeeImage");

};
