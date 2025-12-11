document.addEventListener("alpine:init", () => {
  Alpine.data("segmented_button", (default_value) => ({
    current_checked_id: null,
    current_checked_value: null,
    initInput: function ($el) {
      if ($el.value == default_value) {
        $el.checked = true;
        this.current_checked_id = $el.id;
        this.current_checked_value = $el.value;
        // console.log(this.current_checked_id);
        // console.log(this.current_checked_value);
        // console.log($el.checked);
      } else {
        $el.checked = false;
      }
    },
    inputChecked: function (e) {
      this.current_checked_id = e.target.id;
      this.current_checked_value = e.target.value;
    //   console.log(this.current_checked_value);
    },
    // a label is the one who calls this function
    myInputChecked: function ($el) {
      return $el.getAttribute("for") == this.current_checked_id;
    },
  }));
});
