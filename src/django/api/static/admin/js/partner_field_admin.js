(function($) {
    'use strict';

    function findFieldRow(fieldSelector, fieldClassSelector) {
        const field = $(fieldSelector);

        if (field.length) {
            const row = field
                .closest(`${fieldClassSelector}, tr, .form-row`)
                .first();
            if (row.length) {
                return row;
            }
        }

        if (fieldClassSelector) {
            const fallbackRow = $(fieldClassSelector).first();
            if (fallbackRow.length) {
                return fallbackRow;
            }
        }

        return $();
    }

    function setupPartnerFieldOptionsToggle() {
        const typeField = $('#id_type');

        if (!typeField.length) {
            return false;
        }

        const jsonSchemaFieldRow = findFieldRow(
            '#id_json_schema',
            '.field-json_schema'
        );
        const baseUrlFieldRow = findFieldRow(
            '#id_base_url',
            '.field-base_url'
        );
        const displayTextFieldRow = findFieldRow(
            '#id_display_text',
            '.field-display_text'
        );

        if (
            !jsonSchemaFieldRow.length &&
            !baseUrlFieldRow.length &&
            !displayTextFieldRow.length
        ) {
            return false;
        }

        const toggleFields = function() {
            const shouldShow = typeField.val() === 'object';
            [jsonSchemaFieldRow, baseUrlFieldRow, displayTextFieldRow].forEach(
                function(row) {
                    if (!row.length) {
                        return;
                    }
                    if (shouldShow) {
                        row.show();
                    } else {
                        row.hide();
                    }
                }
            );
        };

        toggleFields();

        typeField.on('change', function() {
            toggleFields();
        });

        return true;
    }

    $(document).ready(function() {
        setupPartnerFieldOptionsToggle();
    });
})(django.jQuery || jQuery);

