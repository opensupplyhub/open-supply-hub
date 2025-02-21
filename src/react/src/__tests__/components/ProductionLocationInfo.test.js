import React from "react";
import { fireEvent } from "@testing-library/react";
import { BrowserRouter as Router } from "react-router-dom";

import ProductionLocationInfo from "../../components/Contribute/ProductionLocationInfo";
import renderWithProviders from "../../util/testUtils/renderWithProviders";

jest.mock("../../components/Filters/StyledSelect", () => (props) => {
    const { options = [], value, onChange, onBlur, placeholder } = props;
    return (
        <select
            data-testid="mocked-select"
            value={value ? value.value : ""}
            onChange={(e) => {
                const selectedOption = options.find(
                    (opt) => opt.value === e.target.value,
                );
                onChange(selectedOption);
            }}
            onBlur={onBlur}
        >
            <option value="">{placeholder}</option>
            {options.map((opt) => (
                <option key={opt.value} value={opt.value}>
                    {opt.label}
                </option>
            ))}
        </select>
    );
});

describe("ProductionLocationInfo component", () => {
    const defaultState = {
        filterOptions: {
            countries: {
                data: [{ value: "US", label: "United States" }],
                error: null,
                fetching: false,
            },
            facilityProcessingType: {
                data: [],
                error: null,
                fetching: false,
            },
        },
    };

    const defaultProps = {
        submitMethod: "POST",
    };

    const renderComponent = (props = {}) => 
        renderWithProviders(
            <Router>
                <ProductionLocationInfo {...defaultProps} {...props} />
            </Router>,
            { preloadedState: defaultState },
        )

    test("renders the production location form", () => {
        const { getByText, getByPlaceholderText, getAllByText, getByTestId } = renderComponent();

        expect(getByText("Production Location Information")).toBeInTheDocument();
        expect(getByText("Use the form below to edit the name, address, and country for your production location.")).toBeInTheDocument();
        expect(getByText("Location Name")).toBeInTheDocument();
        expect(getByText("Enter the name of the production location that you are uploading.")).toBeInTheDocument();
        expect(getByText("Address")).toBeInTheDocument();
        expect(getByText("Enter the address of the production location. We will use this to plot the location on a map.")).toBeInTheDocument();
        expect(getAllByText("Country")).toHaveLength(2);
        expect(getByText("Select the country where the production site is located.")).toBeInTheDocument();
        expect(getByText("Additional information")).toBeInTheDocument();
        expect(
            getByText("Expand this section to add more data about your production location, including product types, number of workers, parent company and more."),
        ).toBeInTheDocument();

        const nameInput = getByPlaceholderText("Enter the name");
        expect(nameInput).toBeInTheDocument();
        expect(nameInput).toHaveValue("");

        const addressInput = getByPlaceholderText("Enter the full address");
        expect(addressInput).toBeInTheDocument();
        expect(addressInput).toHaveValue("");

        const countrySelect = getByTestId("mocked-select");
        expect(countrySelect).toBeInTheDocument();
        expect(countrySelect).toHaveValue("");

        const iconButton = getByTestId("toggle-additional-info");
        expect(iconButton).toBeInTheDocument();
    });

    test("displays error (and disables submit) when required fields are empty after blur", () => {
        const { getByRole, getByPlaceholderText, getAllByText, getByTestId } = renderComponent();

        const submitButton = getByRole("button", { name: /Submit/i });
        expect(submitButton).toBeDisabled();

        const nameInput = getByPlaceholderText("Enter the name");
        const addressInput = getByPlaceholderText("Enter the full address");
        const countrySelect = getByTestId("mocked-select");

        fireEvent.blur(nameInput);
        fireEvent.blur(addressInput);
        fireEvent.blur(countrySelect);

        const nameError = getAllByText("This field is required.");
        expect(nameError).toHaveLength(3);

        expect(getByPlaceholderText("Enter the name")).toHaveAttribute("aria-invalid", "true");
        expect(getByPlaceholderText("Enter the full address")).toHaveAttribute("aria-invalid", "true");
    });

    test("enables the submit button when required fields are filled", () => {
        const { getByRole, getByPlaceholderText, getByTestId } = renderComponent();

        const submitButton = getByRole("button", { name: /Submit/i });
        expect(submitButton).toBeDisabled();

        const nameInput = getByPlaceholderText("Enter the name");
        const addressInput = getByPlaceholderText("Enter the full address");
        const countrySelect = getByTestId("mocked-select");

        fireEvent.change(nameInput, { target: { value: "Test Name" } });
        fireEvent.change(addressInput, { target: { value: "Test Address" } });
        fireEvent.change(countrySelect, { target: { value: "US" } });

        expect(countrySelect.value).toBe("US");
        expect(submitButton).toBeEnabled();
    });

    test("displays additional information form when icon button is clicked", () => {
        const { getByTestId, getByText, queryByText } = renderComponent();

        const iconButton = getByTestId("toggle-additional-info");
        fireEvent.click(iconButton);

        expect(getByText("Sector(s)")).toBeInTheDocument();
        expect(getByText("Select the sector(s) that this location operates in. For example: Apparel, Electronics, Renewable Energy.")).toBeInTheDocument();
        expect(getByText("Product Type(s)")).toBeInTheDocument();
        expect(getByText("Enter the type of products produced at this location. For example: Shirts, Laptops, Solar Panels.")).toBeInTheDocument();
        expect(getByText("Location Type(s)")).toBeInTheDocument();
        expect(getByText("Select the location type(s) for this production location. For example: Final Product Assembly, Raw Materials Production or Processing, Office/HQ.")).toBeInTheDocument();
        expect(getByText("Processing Type(s)")).toBeInTheDocument();
        expect(getByText("Select the type of processing activities that take place at this location. For example: Printing, Tooling, Assembly.")).toBeInTheDocument();
        expect(getByText("Number of Workers")).toBeInTheDocument();
        expect(getByText("Enter a number or a range for the number of people employed at the location. For example: 100, 100-150.")).toBeInTheDocument();
        expect(getByText("Parent Company")).toBeInTheDocument();
        expect(getByText("Enter the company that holds majority ownership for this production.")).toBeInTheDocument();

        fireEvent.click(iconButton);

        expect(queryByText("Sector(s)")).not.toBeInTheDocument();
        expect(queryByText("Product Type(s)")).not.toBeInTheDocument();
        expect(queryByText("Location Type(s)")).not.toBeInTheDocument();
        expect(queryByText("Processing Type(s)")).not.toBeInTheDocument();
        expect(queryByText("Number of Workers")).not.toBeInTheDocument();
        expect(queryByText("Parent Company")).not.toBeInTheDocument();
    });

    test("displays error when number of workers is not a valid number and disable submit button", () => {
        const { getByRole, getByPlaceholderText, getByTestId } = renderComponent();

        const submitButton = getByRole("button", { name: /Submit/i });
        expect(submitButton).toBeDisabled();

        const nameInput = getByPlaceholderText("Enter the name");
        const addressInput = getByPlaceholderText("Enter the full address");
        const countrySelect = getByTestId("mocked-select");

        fireEvent.change(nameInput, { target: { value: "Test Name" } });
        fireEvent.change(addressInput, { target: { value: "Test Address" } });
        fireEvent.change(countrySelect, { target: { value: "US" } });

        expect(submitButton).toBeEnabled();

        const iconButton = getByTestId("toggle-additional-info");
        fireEvent.click(iconButton);

        const numberInput = getByPlaceholderText("Enter the number of workers as a number or range");
        fireEvent.change(numberInput, { target: { value: "Test" } });

        expect(getByPlaceholderText("Enter the number of workers as a number or range")).toHaveAttribute("aria-invalid", "true");
        expect(submitButton).toBeDisabled();

        fireEvent.change(numberInput, { target: { value: "100" } });

        expect(getByPlaceholderText("Enter the number of workers as a number or range")).toHaveAttribute("aria-invalid", "false");
        expect(submitButton).toBeEnabled();

        fireEvent.change(numberInput, { target: { value: "100-150" } });

        expect(getByPlaceholderText("Enter the number of workers as a number or range")).toHaveAttribute("aria-invalid", "false");
        expect(submitButton).toBeEnabled();

        fireEvent.change(numberInput, { target: { value: "200-100" } });

        expect(getByPlaceholderText("Enter the number of workers as a number or range")).toHaveAttribute("aria-invalid", "true");
        expect(submitButton).toBeDisabled
    });
});
