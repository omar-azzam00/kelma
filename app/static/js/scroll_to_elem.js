function scrollToElem(elem) {
  let distanceToTop = window.pageYOffset + elem.getBoundingClientRect().top;
  window.scrollTo({ top: distanceToTop - 16, left: 0, behavior: "smooth" });
}
