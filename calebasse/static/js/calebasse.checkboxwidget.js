if(typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function() 
    {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

(function ($, undefined) {
  $.widget('eo.checkboxwidget', {
    options: {
      noneCaption: "Aucun",
      allCaption: undefined,
    },
    _create: function () {
       this.state = 0;
       this.visible = this.element.is(':visible');
       this.elements = [];
       var inputs = $('input[type="checkbox"]', this.element)
       this.placeholder = $('<div></div>')
             .css('position', 'relative')
             .addClass('eo-checkboxwidget-placeholder');
       this.selection = $('<span></span>')
             .addClass('eo-checkboxwidget-selection')
             .appendTo(this.placeholder);
       this.element.before(this.placeholder);
       this.menu = $('<div></div>')
             .addClass('eo-checkboxwidget-menu')
             .css('position', 'fixed')
             .hide()
             .appendTo(this.placeholder);
       for (var i = 0; i < inputs.length; i++) {
         var $input = $(inputs[i]);
         var content = $input.closest('label').text().trim();
         var $menu_element = $('<div></div>')
               .addClass('eo-checkboxwidget-menu-element')
               .text(content)
               .data('input', $input)
               .appendTo(this.menu);
         if ($input.is(':checked')) {
           $menu_element.addClass('eo-checkboxwidget-menu-element-selected');
         }
         this.elements.push({
           menu_element: $menu_element,
           content: content,
           input: $input
         });
       }
       this.menu.on('click', '.eo-checkboxwidget-menu-element', $.proxy(function (e) {
         var $menu_element = $(e.target);
         var $input = $menu_element.data('input');
         var checked = $input.is(':checked');
         $menu_element.toggleClass('eo-checkboxwidget-menu-element-selected',
           ! checked);
         $input.prop('checked', ! checked);
         $input.trigger('change');
         this._refresh();
       }, this));
       /* this.menu.closest('body').on('click.eo-checkboxwidget', $.proxy(function (e) {
         if ($(e.target).closest(this.element).length == 0) {
           this.menu.toggle();
         }
       }, this)); */
       this.placeholder.on('mousemove.eo-checkboxwidget', $.proxy(function () {
         if (this.__proto__.block == 1) {
           return true;
         }
         this.__proto__.block = 1;
         this.state = 1;
         this.menu.show();
         var placeholder_top = this.placeholder.offset().top-$(document).scrollTop();
         if (placeholder_top < (window.innerHeight/2)) {
           this.menu.css('top', placeholder_top+this.placeholder.outerHeight(true));
         } else {
           this.menu
               .css('top', placeholder_top-this.menu.outerHeight(true));
         }
         return false;
       }, this))
       this.element.hide();
       this.menu.on('mouseleave', $.proxy(function () {
           setTimeout($.proxy(function () { 
             this.__proto__.block = 0 
           }, this), 100);
           this.state = 0;
           this.menu.hide();
         }, this)
       );
    },
    _init: function() {
       this._refresh();
    },
    _refresh: function () {
       this.selection.html('');
       var checked = [];
       for (var i = 0; i < this.elements.length; i++) {
         if (this.elements[i].input.is(':checked')) {
           checked.push(i);
         }
       }
       if (checked.length == this.elements.length && this.options.allCaption) {
         this.selection.append(this.options.allCaption);
       } else if (checked.length) {
         for (var i = 0; i < checked.length; i++) {
           var content = this.elements[checked[i]].content;
           var $caption = $('<span>'+content+'</span>')
              .addClass('eo-checkboxwidget-caption');
           $caption.appendTo(this.selection);
           if (i != (checked.length-1)) {
             this.selection.append(', ');
           }
         }
       } else {
         this.selection.append(this.options.noneCaption);
       }
    },
    destroy: function () {
       $.Widget.prototype.destroy.call(this);
       this.placeholder.remove();
       if (this.visible) {
         this.element.show();
       }
    }
  })
})(window.jQuery)
