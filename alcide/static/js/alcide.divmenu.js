(function ($, undefined) {
  $.widget('eo.divmenu', {
    options: {
    },
    _create: function () {
      this.elements = $('> *', this.element);
      this._select = 0;
    },
    _closed: 1,
    _opened: 0,
    _init: function() {
      this.element.addClass('eo-divmenu-container');
      this.elements.addClass('eo-divmenu-element');
      this.element.on('change.eo-divmenu', '.eo-divmenu-element input, .eo-divmenu-element select',
        $.proxy(function (e) {
          $('input, select', this.element).not(e.target).val('');
          this._refresh();
        }, this)
      );
      this.state = this.closed;
      this._refresh();
    },
    open: function () {
      this.state = this._opened;
      var new_height = 0;
      for (var i = 0; i < this.elements.length; i++) {
        new_height += $(this.elements.get(i)).outerHeight(true);
      }
      this.element.animate({ height: new_height });
    },
    close: function () {
      this.state = this.closed;
      var $selected = $(this.elements.get(this._select));
      /* Move element in place */
      var scrollTop = 0;
      if (this.element.css('position') != 'static') {
        scrollTop = $selected.position().top + this.element.scrollTop();
      } else {
        scrollTop = $selected.position().top - this.element.position().top + this.element.scrollTop();
      }
      var new_properties = {
        height: $selected.outerHeight(true),
        width: $selected.outerWidth(true),
        scrollTop: scrollTop,
      };
      this.element.animate(new_properties);
    },
    toggle: function () {
      if (this.state == this.closed) {
        this.open();
      } else {
        this.close();
      }
    },
    select: function (i) {
      if (typeof(i) != 'number') {
        i = this.elements.index(i);
      }
      this._select = i;
      this._refresh();
    },
    _refresh: function () {
      if (this.state == this.closed) {
        this.close();
      }
    },
    destroy: function () {
      this.element.removeClass('eo-divmenu-container');
      this.elements.removeClass('eo-divmenu-element');
      $('*', this.element).off('.eo-divmenu');
    }
  })
})(window.jQuery)
