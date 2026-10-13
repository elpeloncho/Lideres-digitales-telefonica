// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { BrowserRouter } from "react-router-dom";
import App from "./App";

vi.mock("./components/MapView", () => ({
  default: () => <div aria-label="Mapa de demostración" />,
}));

afterEach(() => {
  cleanup();
  window.history.replaceState({}, "", "/");
});

describe("perfiles y ventanas del prototipo", () => {
  it("muestra la navegación propia del perfil de operaciones", () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>,
    );

    fireEvent.change(screen.getByLabelText("Cambiar perfil de demostración"), {
      target: { value: "operations" },
    });

    expect(screen.getByRole("link", { name: /alertas/i })).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /bandeja de triaje/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: /mapa de incidencias/i }),
    ).not.toBeInTheDocument();
  });

  it("mantiene la página de reportes aislada de la navegación técnica", () => {
    window.history.replaceState({}, "", "/reportar");
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>,
    );

    expect(
      screen.getByRole("heading", { name: "Comunica una incidencia" }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("navigation", { name: "Navegación principal" }),
    ).not.toBeInTheDocument();
    expect(screen.getByText(/solo registra avisos sintéticos/i)).toBeInTheDocument();
  });
});
