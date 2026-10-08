document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-copy-contact]");
  if (!button) return;
  const contact = button.dataset.copyContact;
  try {
    await navigator.clipboard.writeText(contact);
    button.textContent = "已复制";
    window.setTimeout(() => { button.textContent = "复制"; }, 1600);
  } catch (_error) {
    button.textContent = "请手动复制";
  }
});
