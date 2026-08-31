(function () {
    function setAccordionState(container, open) {
        if (!container) {
            return;
        }

        container.querySelectorAll('details').forEach(function (details) {
            details.open = open;
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var accordion = document.querySelector('[data-isic-accordion]');
        var expandAll = document.querySelector('[data-isic-expand-all]');
        var collapseAll = document.querySelector('[data-isic-collapse-all]');

        if (expandAll) {
            expandAll.addEventListener('click', function () {
                setAccordionState(accordion, true);
            });
        }

        if (collapseAll) {
            collapseAll.addEventListener('click', function () {
                setAccordionState(accordion, false);
            });
        }
    });
}());
