class RangeField {
  constructor($element) {
    this.$element = $element;
    this.$range_input = this.$element.find('.range-input');
    this.$value_output = this.$element.find('.value-output');
    this.syncValueOutput();
    this.$range_input.on('input', () => {
      this.syncValueOutput();
    });
  }

  syncValueOutput() {
    this.$value_output.val(this.$range_input.val());
  }
}
