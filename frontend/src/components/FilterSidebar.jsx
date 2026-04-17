import { useState, useRef, useEffect } from "react";

function FilterSidebar({ filters, selected, onChange }) {
    const [locationOpen, setLocationOpen] = useState(false);
    const [locationSearch, setLocationSearch] = useState("");
    const locationRef = useRef(null);

    const locations = filters.locations || [];
    const educationLevels = filters.education_levels || [];

    useEffect(() => {
        function handleClickOutside(e) {
            if (locationRef.current && !locationRef.current.contains(e.target)) {
                setLocationOpen(false);
            }
        }

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const filteredLocations = locations.filter((location) =>
        location.toLowerCase().includes(locationSearch.toLowerCase())
    );

    function toggleLocation(location) {
        const nextLocations = selected.locations.includes(location)
            ? selected.locations.filter((item) => item !== location)
            : [...selected.locations, location];

        onChange({
            ...selected,
            locations: nextLocations,
        });
    }

    function setEducation(level) {
        onChange({
            ...selected,
            education: selected.education === level ? null : level,
        });
    }

    function setExperienceRange(minExp, maxExp) {
        const isSameRange =
            selected.minExp === minExp && selected.maxExp === maxExp;

        onChange({
            ...selected,
            minExp: isSameRange ? null : minExp,
            maxExp: isSameRange ? null : maxExp,
        });
    }

    function clearAll() {
        onChange({
            locations: [],
            education: null,
            minExp: null,
            maxExp: null,
        });
    }

    function isActiveRange(minExp, maxExp) {
        return selected.minExp === minExp && selected.maxExp === maxExp;
    }

    return (
        <div className="card">
            <h2>Filters</h2>

            <div className="filter-section">
                <h3>Location</h3>
                <div className="select-wrapper" ref={locationRef}>
                    <div
                        className="select-input"
                        onClick={() => setLocationOpen(!locationOpen)}
                    >
                        {selected.locations.length > 0 ? (
                            <div className="selected-tags">
                                {selected.locations.map((location) => (
                                    <span key={location} className="selected-tag">
                                        {location}
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                toggleLocation(location);
                                            }}
                                        >
                                            ×
                                        </button>
                                    </span>
                                ))}
                            </div>
                        ) : (
                            <span className="select-placeholder">
                                Search or select locations...
                            </span>
                        )}
                        <span className="select-arrow">{locationOpen ? "▲" : "▼"}</span>
                    </div>

                    {locationOpen && (
                        <div className="select-dropdown">
                            <input
                                className="select-search"
                                type="text"
                                placeholder="Type to search..."
                                value={locationSearch}
                                onChange={(e) => setLocationSearch(e.target.value)}
                                autoFocus
                            />
                            <div className="select-options">
                                {filteredLocations.map((location) => (
                                    <div
                                        key={location}
                                        className={`select-option ${selected.locations.includes(location) ? "selected" : ""
                                            }`}
                                        onClick={() => toggleLocation(location)}
                                    >
                                        <span>{location}</span>
                                        {selected.locations.includes(location) && (
                                            <span className="checkmark">✓</span>
                                        )}
                                    </div>
                                ))}
                                {filteredLocations.length === 0 && (
                                    <div className="select-option disabled">
                                        No locations found
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <div className="filter-section">
                <h3>Education</h3>
                {educationLevels.length > 0 ? (
                    educationLevels.map((level) => (
                        <label key={level} className="filter-checkbox">
                            <input
                                type="checkbox"
                                checked={selected.education === level}
                                onChange={() => setEducation(level)}
                            />
                            <span>{level.toUpperCase()}</span>
                        </label>
                    ))
                ) : (
                    <p className="empty-state">No education filters available yet.</p>
                )}
            </div>

            <div className="filter-section">
                <h3>Experience</h3>
                <div className="filter-range">
                    <button
                        type="button"
                        className={isActiveRange(0, 2) ? "active" : ""}
                        onClick={() => setExperienceRange(0, 2)}
                    >
                        0-2 yrs
                    </button>
                    <button
                        type="button"
                        className={isActiveRange(3, 5) ? "active" : ""}
                        onClick={() => setExperienceRange(3, 5)}
                    >
                        3-5 yrs
                    </button>
                    <button
                        type="button"
                        className={isActiveRange(5, 10) ? "active" : ""}
                        onClick={() => setExperienceRange(5, 10)}
                    >
                        5-10 yrs
                    </button>
                    <button
                        type="button"
                        className={isActiveRange(10, null) ? "active" : ""}
                        onClick={() => setExperienceRange(10, null)}
                    >
                        10+ yrs
                    </button>
                </div>
            </div>

            <button type="button" className="scrape-btn clear-filters" onClick={clearAll}>
                Clear All
            </button>
        </div>
    );
}

export default FilterSidebar;
