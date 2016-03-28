$(function () {
  $('body').on('mousewheel', '.mousewheel', function (event, delta) {
    var increment = parseInt($(this).data('mousewheel-increment'));
    var lo = parseInt($(this).data('mousewheel-lo')) || 0;
    var hi = parseInt($(this).data('mousewheel-hi')) || 1000;
    var $this = $(this);
    if (delta < 0) {
      increment = -increment;
    }
    if ($this.is('input')) {
      value = $this.val();
    } else {
      value = $this.text();
    }
    try {
      value = parseInt(value || 0);
    } catch (e) {
      value = 0;
    }
    value += increment;
    if (value < lo) {
      value = lo;
    } else if (value > hi) {
      value = hi;
    }
    if ($this.is('input')) {
      $this.val(value);
    } else {
      $this.html(value);
    }
    return false;
  });
});
