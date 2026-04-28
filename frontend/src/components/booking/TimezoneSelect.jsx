/* eslint-disable react/prop-types */
import { useEffect, useMemo, useState } from "react";
import Select from "react-select";

import { formatTimezoneCurrentTime, formatTimezoneDisplay } from "../../utils/dateTime.js";

const TIMEZONE_SELECT_STYLES = {
  control: (baseStyles, state) => ({
    ...baseStyles,
    borderColor: state.isFocused ? "var(--accent)" : "#c9d0da",
    borderRadius: 6,
    boxShadow: state.isFocused ? "0 0 0 3px var(--focus)" : "none",
    color: "var(--text)",
    font: "inherit",
    minHeight: 44,
    "&:hover": {
      borderColor: state.isFocused ? "var(--accent)" : "#aab4c1",
    },
  }),
  indicatorSeparator: (baseStyles) => ({
    ...baseStyles,
    backgroundColor: "#d6d9de",
  }),
  input: (baseStyles) => ({
    ...baseStyles,
    color: "var(--text)",
  }),
  menu: (baseStyles) => ({
    ...baseStyles,
    zIndex: 10,
  }),
  menuPortal: (baseStyles) => ({
    ...baseStyles,
    zIndex: 20,
  }),
  option: (baseStyles, state) => ({
    ...baseStyles,
    backgroundColor: state.isSelected ? "var(--accent)" : state.isFocused ? "#eef5ff" : "#ffffff",
    color: state.isSelected ? "#ffffff" : "var(--text)",
    cursor: "pointer",
  }),
  placeholder: (baseStyles) => ({
    ...baseStyles,
    color: "var(--muted)",
  }),
  singleValue: (baseStyles) => ({
    ...baseStyles,
    color: "var(--text)",
  }),
  valueContainer: (baseStyles) => ({
    ...baseStyles,
    padding: "0 12px",
  }),
};

function TimezoneOptionLabel({ currentTime, label }) {
  return (
    <span className="timezone-select-option">
      <span className="timezone-select-option-name">{label}</span>
      <span className="timezone-select-option-time">{currentTime}</span>
    </span>
  );
}

export default function TimezoneSelect({ onChange, timezones, value }) {
  const [currentDate, setCurrentDate] = useState(() => new Date());
  const menuPortalTarget = typeof document === "undefined" ? undefined : document.body;
  const options = useMemo(
    () =>
      timezones.map((timezone) => ({
        currentTime: formatTimezoneCurrentTime(timezone, currentDate),
        label: formatTimezoneDisplay(timezone),
        value: timezone,
      })),
    [currentDate, timezones],
  );
  const selectedOption = options.find((option) => option.value === value) || null;

  useEffect(() => {
    const intervalId = window.setInterval(() => setCurrentDate(new Date()), 60000);

    return () => window.clearInterval(intervalId);
  }, []);

  return (
    <div className="timezone-select">
      <label className="timezone-select-label" htmlFor="booking-timezone-select">
        Time zone
      </label>
      <Select
        classNamePrefix="timezone-select"
        formatOptionLabel={(option) => <TimezoneOptionLabel {...option} />}
        inputId="booking-timezone-select"
        isSearchable
        menuPortalTarget={menuPortalTarget}
        menuPosition="fixed"
        noOptionsMessage={() => "No time zones found"}
        onChange={(option) => {
          if (option) {
            onChange(option.value);
          }
        }}
        options={options}
        styles={TIMEZONE_SELECT_STYLES}
        value={selectedOption}
      />
    </div>
  );
}
