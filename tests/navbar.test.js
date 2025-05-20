import '@testing-library/jest-dom/extend-expect';

describe("Navbar scroll and toggle behavior", () => {
  let navbar, scrollTopBtn, navbarToggler, navbarCollapse;

  beforeEach(() => {
    document.body.innerHTML = `
      <div class="navbar"></div>
      <button id="scrollTopBtn" class="d-none"></button>
      <button class="navbar-toggler"></button>
      <div class="navbar-collapse show"></div>
      <nav class="navbar-nav">
        <a href="#">Link1</a>
        <a href="#">Link2</a>
      </nav>
    `;

    navbar = document.querySelector(".navbar");
    scrollTopBtn = document.getElementById("scrollTopBtn");
    navbarToggler = document.querySelector(".navbar-toggler");
    navbarCollapse = document.querySelector(".navbar-collapse");

    let lastScrollTop = 0;
    const scrollLimit = 150;
    const mobileLimit = 992;

    window.addEventListener("scroll", () => {
      let currentScroll = window.scrollY;
      const isScrollingDown = currentScroll > lastScrollTop && currentScroll > scrollLimit;
      const isNavOpen = document.body.classList.contains("nav-open");

      navbar.classList.toggle("fixed-top", !(isScrollingDown && !isNavOpen));
      scrollTopBtn.classList.toggle("fixed-bottom", currentScroll > scrollLimit && !isNavOpen);
      scrollTopBtn.classList.toggle("d-none", currentScroll < scrollLimit || isNavOpen);

      lastScrollTop = Math.max(0, currentScroll);
    });

    navbarToggler.addEventListener("click", () => {
      document.body.classList.toggle("nav-open");
      const isNavOpen = document.body.classList.contains("nav-open");
      scrollTopBtn.classList.toggle("d-none", isNavOpen || window.scrollY < scrollLimit);
    });

    document.querySelectorAll(".navbar-nav a").forEach(link => {
      link.addEventListener("click", () => {
        if (window.innerWidth < mobileLimit) {
          navbarCollapse.classList.remove("show");
          document.body.classList.remove("nav-open");
        }
      });
    });
  });

  test("scroll down over limit adds/removes classes correctly", () => {
    Object.defineProperty(window, 'scrollY', { value: 200, writable: true });

    window.dispatchEvent(new Event('scroll'));

    expect(navbar).toHaveClass("fixed-top");
    expect(scrollTopBtn).toHaveClass("fixed-bottom");
    expect(scrollTopBtn).not.toHaveClass("d-none");

    window.scrollY = 100;
    window.dispatchEvent(new Event('scroll'));

    expect(navbar).not.toHaveClass("fixed-top");
  });

  test("click toggler toggles nav-open class and scrollTopBtn visibility", () => {
    Object.defineProperty(window, 'scrollY', { value: 0, writable: true });

    navbarToggler.click();

    expect(document.body).toHaveClass("nav-open");
    expect(scrollTopBtn).toHaveClass("d-none");

    navbarToggler.click();

    expect(document.body).not.toHaveClass("nav-open");
  });

  test("click link removes show class and nav-open on mobile", () => {
    Object.defineProperty(window, 'innerWidth', { value: 500, writable: true });

    navbarCollapse.classList.add("show");
    document.body.classList.add("nav-open");

    const link = document.querySelector(".navbar-nav a");
    link.click();

    expect(navbarCollapse).not.toHaveClass("show");
    expect(document.body).not.toHaveClass("nav-open");
  });
});
