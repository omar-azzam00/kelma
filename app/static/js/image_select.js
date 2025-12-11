document.addEventListener("alpine:init", () => {
  Alpine.data("image_select", (server_image_url) => {
    return {
      hovered: false,
      image_data: server_image_url,
      updateSelect: function (image_file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          // console.log(this.image_data);
          this.image_data = e.target.result;
          // console.log(this.image_data);
        };
        reader.onerror = (e) => {
          alert("حدتث مشكله أثناء تحميل هذه الصوره!");
        };
        reader.readAsDataURL(image_file);
      },
    };
  });
});
