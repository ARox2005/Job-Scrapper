function FilterSidebar({ filters, selected, onChange }) {
    const locations = filters.locations || [];
    const educationLevels = filters.education_levels || [];

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

    return (
        <div className="card">
            <h2>Filters</h2>

            <div className="filter-section">
                <h3>Location</h3>
                {locations.length > 0 ? (
                    locations.map((location) => (
                        <label key={location} className="filter-checkbox">
                            <input
                                type="checkbox"
                                checked={selected.locations.includes(location)}
                                onChange={() => toggleLocation(location)}
                            />
                            <span>{location}</span>
                        </label>
                    ))
                ) : (
                    <p className="empty-state">No locations available yet.</p>
                )}
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
                    <button type="button" onClick={() => setExperienceRange(0, 2)}>
                        0-2 yrs
                    </button>
                    <button type="button" onClick={() => setExperienceRange(3, 5)}>
                        3-5 yrs
                    </button>
                    <button type="button" onClick={() => setExperienceRange(5, 10)}>
                        5-10 yrs
                    </button>
                    <button type="button" onClick={() => setExperienceRange(10, null)}>
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
