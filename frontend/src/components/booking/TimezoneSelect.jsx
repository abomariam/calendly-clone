/* eslint-disable react/prop-types */
import { formatTimezoneDisplay } from "../../utils/dateTime.js";

export default function TimezoneSelect({ onChange, timezones, value }) {
  return (
    <label className="timezone-select">
      Time zone
      <select onChange={(event) => onChange(event.target.value)} value={value}>
        {timezones.map((timezone) => (
          <option key={timezone} value={timezone}>
            {formatTimezoneDisplay(timezone)}
          </option>
        ))}
      </select>
    </label>
  );
}
