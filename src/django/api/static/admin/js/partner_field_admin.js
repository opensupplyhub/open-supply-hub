(function($) {
    'use strict';

    function findJsonSchemaFieldRow() {
        var jsonSchemaField = $('#id_json_schema');
        
        if (jsonSchemaField.length) {
            return jsonSchemaField.closest('.field-json_schema, tr, .form-row').first();
        }
        
        return $('.field-json_schema').first();
    }

    function toggleJsonSchemaField() {
        var typeField = $('#id_type');
        var jsonSchemaFieldRow = findJsonSchemaFieldRow();
        
        if (!typeField.length) {
            return false;
        }
        
        if (!jsonSchemaFieldRow.length) {
            return false;
        }
        
        var currentType = typeField.val();
        
        if (currentType === 'object') {
            jsonSchemaFieldRow.show();
            return true;
        } else {
            jsonSchemaFieldRow.hide();
            return true;
        }
    }

    function setupJsonSchemaToggle() {
        var typeField = $('#id_type');
        var jsonSchemaField = $('#id_json_schema');
        
        if (!typeField.length || !jsonSchemaField.length) {
            return false;
        }
        
        var jsonSchemaFieldRow = findJsonSchemaFieldRow();
        if (!jsonSchemaFieldRow.length) {
            return false;
        }
        
        toggleJsonSchemaField();
        
        typeField.on('change', function() {
            toggleJsonSchemaField();
        });
        
        return true;
    }

    $(document).ready(function() {
        setupJsonSchemaToggle();
    });
})(django.jQuery || jQuery);

