document.addEventListener("alpine:init", () => {
  Alpine.data("kelmas_state", kelmasState);
});

function kelmasState(targetSelector, kelmaTemplateSelector, start, size) {
  let target = document.querySelector(targetSelector);
  let kelmaBlueprint = document.querySelector(kelmaTemplateSelector).content
    .firstElementChild;
  if (start === undefined) {
    start = 0;
  }
  if (size === undefined) {
    let setSize = () => {
      size = Math.floor(window.innerWidth / 75) * 5;
    };
    setSize();
    window.addEventListener("resize", setSize);
  }
  let first = true;

  return {
    empty: false,
    finished: false,
    loading: true,
    // this function add no duplicate kelmas to the list.
    async addKelmas() {
      this.loading = true;

      let newKelmas = await getKelmas(start, size, 0);

      newKelmas.forEach((kelma) => {
        let newKelmaElem = kelmaBlueprint.cloneNode(true);
        newKelmaElem.setAttribute(
          "x-data",
          `{ "kelma": ${JSON.stringify(kelma)} }`,
        );
        target.appendChild(newKelmaElem);
      });

      if (newKelmas.length == 0) {
        this.finished = true;
        if (first) {
          this.empty = true;
        }
      }
      start += newKelmas.length;
      first = false;
      this.loading = false;
    },
  };
}