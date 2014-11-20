var AdminFilters = function(element, filtersElement, filterGroups) {
    var $root = $(element);
    var $container = $('.filters', $root);
    var lastCount = 0;

    function getCount(name) {
        var idx = name.indexOf('_');

        if (idx === -1) {
            return 0;
        }

        return parseInt(name.substr(3, idx - 3), 10);
    }

    function makeName(name) {
        var result = 'flt' + lastCount + '_' + name;
        lastCount += 1;
        return result;
    }

    function changeOperation() {
        var $row = $(this).closest('tr');
        var $el = $('.filter-val:input', $row);
        var count = getCount($el.attr('name'));
        $el.attr('name', 'flt' + count + '_' + $(this).val());
        $('button', $root).show();
    }

    function removeFilter() {
        $(this).closest('tr').remove();
        if($('.filters tr').length == 0) {
            $('button', $root).hide();
            $('a[class=btn]', $root).hide();
            $('.filters tbody').remove();
        } else {
            $('button', $root).show();
        }
        
        return false;
    }

    function addFilter(name, subfilters) {
        var $el = $('<tr />').appendTo($container);

        // Filter list
        $el.append(
            $('<td/>').append(
                $('<a href="#" class="btn btn-filter remove-filter" />')
                    .append($('<span class="close-icon">&times;</span>'))
                    .append('&nbsp;')
                    .append(name)
                    .click(removeFilter)
                )
        );

        // Filter type
        var $select = $('<select class="filter-op" />')
                      .change(changeOperation);

        $(subfilters).each(function() {
            $select.append($('<option/>').attr('value', this.arg).text(this.operation));
        });

        $el.append(
            $('<td/>').append($select)
        );

        // on change, get the subfilter based on the index of the added element, then modify the input field (turn into date range if necessary)
        $select.select2({width: 'resolve'}).on("change", function(e) { styleFilterInput(subfilters[e.added.element[0].index], $el.find('input').last()); });

        // add styling to input field, accommodates filters that change the type of the field 
        function styleFilterInput(filter, field) {
            if (filter.type) {
                field.attr('data-role', filter.type);
                if ((filter.type == "datepicker") || (filter.type == "daterangepicker")) {
                    field.attr('data-date-format', "YYYY-MM-DD");
                }
                else if ((filter.type == "datetimepicker") || (filter.type == "datetimerangepicker")) {
                    field.attr('data-date-format', "YYYY-MM-DD HH:mm:ss");
                }
                else if ((filter.type == "timepicker")  || (filter.type == "timerangepicker")) {
                    field.attr('data-date-format', "HH:mm:ss");
                }
                faForm.applyStyle(field, filter.type);
            }
        }
        
        // initial filter creation
        filter = subfilters[0];
        var $field;

        if (filter.options) {
            $field = $('<select class="filter-val" />')
                        .attr('name', makeName(filter.arg));

            $(filter.options).each(function() {
                $field.append($('<option/>')
                    .val(this[0]).text(this[1]));
            });

            $el.append($('<td/>').append($field));
            $field.select2({width: 'resolve'});
        } else
        {
            $field = $('<input type="text" class="filter-val form-control" />')
                        .attr('name', makeName(filter.arg));
            $el.append($('<td/>').append($field));
        }
        
        styleFilterInput(filter, $field);
    }

    $('a.filter', filtersElement).click(function() {
        var name = ($(this).text().trim !== undefined ? $(this).text().trim() : $(this).text().replace(/^\s+|\s+$/g,''));

        addFilter(name, filterGroups[name]);

        $('button', $root).show();

        //return false;
    });

    $('.filter-op', $root).change(changeOperation);
    $('.filter-val', $root).change(function() {
        $('button', $root).show();
    });
    $('.remove-filter', $root).click(removeFilter);

    $('.filter-val', $root).each(function() {
        var count = getCount($(this).attr('name'));
        if (count > lastCount)
            lastCount = count;
    });

    lastCount += 1;
};
