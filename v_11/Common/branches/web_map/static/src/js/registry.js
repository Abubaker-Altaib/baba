odoo.define('web_map._custom_field_registry', function (require) {
    "use strict";

    
    var registry = require('web.field_registry');


    var FieldMap = require('web_map.FieldMap');


    // Special fields
    registry
        .add('map', FieldMap.FieldMap);
});