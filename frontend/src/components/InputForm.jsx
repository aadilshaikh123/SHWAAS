import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MapPin, Loader2, AlertCircle, Search, User, Navigation } from 'lucide-react'
import { searchCities, getCityByName } from '../data/cities'

function InputForm({ darkMode, formData, setFormData, onSubmit, loading, error }) {
    const [gettingLocation, setGettingLocation] = useState(false)
    const [locationError, setLocationError] = useState(null)
    const [cityQuery, setCityQuery] = useState(formData.city || '')
    const [suggestions, setSuggestions] = useState([])
    const [showSuggestions, setShowSuggestions] = useState(false)
    const [selectedIndex, setSelectedIndex] = useState(-1)
    const inputRef = useRef(null)
    const suggestionsRef = useRef(null)

    // Handle city input change
    const handleCityChange = (e) => {
        const value = e.target.value
        setCityQuery(value)

        if (value.length >= 2) {
            const results = searchCities(value)
            setSuggestions(results)
            setShowSuggestions(true)
            setSelectedIndex(-1)
        } else {
            setSuggestions([])
            setShowSuggestions(false)
        }
    }

    // Handle city selection
    const selectCity = (city) => {
        setCityQuery(city.name)
        setFormData(prev => ({
            ...prev,
            city: city.name,
            lat: city.lat,
            lon: city.lon
        }))
        setSuggestions([])
        setShowSuggestions(false)
        setLocationError(null)
    }

    // Handle keyboard navigation
    const handleKeyDown = (e) => {
        if (!showSuggestions || suggestions.length === 0) return

        if (e.key === 'ArrowDown') {
            e.preventDefault()
            setSelectedIndex(prev =>
                prev < suggestions.length - 1 ? prev + 1 : prev
            )
        } else if (e.key === 'ArrowUp') {
            e.preventDefault()
            setSelectedIndex(prev => prev > 0 ? prev - 1 : -1)
        } else if (e.key === 'Enter' && selectedIndex >= 0) {
            e.preventDefault()
            selectCity(suggestions[selectedIndex])
        } else if (e.key === 'Escape') {
            setShowSuggestions(false)
        }
    }

    // Close suggestions when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (
                suggestionsRef.current &&
                !suggestionsRef.current.contains(event.target) &&
                inputRef.current &&
                !inputRef.current.contains(event.target)
            ) {
                setShowSuggestions(false)
            }
        }

        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }))
    }

    const useMyLocation = async () => {
        if (!navigator.geolocation) {
            setLocationError('Geolocation is not supported by your browser')
            return
        }

        setGettingLocation(true)
        setLocationError(null)

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude
                const lon = position.coords.longitude

                // Try to get city name from reverse geocoding
                try {
                    const response = await fetch(
                        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=10`
                    )
                    const data = await response.json()

                    const cityName = data.address?.city ||
                        data.address?.town ||
                        data.address?.village ||
                        data.address?.state ||
                        'Current Location'

                    setCityQuery(cityName)
                    setFormData(prev => ({
                        ...prev,
                        city: cityName,
                        lat: lat,
                        lon: lon
                    }))
                } catch (err) {
                    // Fallback if reverse geocoding fails
                    setCityQuery('Current Location')
                    setFormData(prev => ({
                        ...prev,
                        city: 'Current Location',
                        lat: lat,
                        lon: lon
                    }))
                }

                setGettingLocation(false)
            },
            (error) => {
                setLocationError('Unable to retrieve your location. Please enable location access.')
                setGettingLocation(false)
            }
        )
    }

    const handleSubmit = (e) => {
        e.preventDefault()

        // Validate that we have coordinates
        if (!formData.lat || !formData.lon) {
            setLocationError('Please select a city or use your current location')
            return
        }

        onSubmit(formData)
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className={`rounded-3xl shadow-2xl p-6 sm:p-8 transition-all duration-300 ${darkMode ? 'glass-dark' : 'glass bg-white/80'
                }`}
        >
            <h2
                className={`text-2xl sm:text-3xl font-bold mb-6 transition-colors duration-300 ${darkMode ? 'text-white' : 'text-gray-900'
                    }`}
            >
                Select Location
            </h2>

            <form onSubmit={handleSubmit} className="space-y-5">
                {/* Auto-detect Location Button */}
                <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    type="button"
                    onClick={useMyLocation}
                    disabled={gettingLocation}
                    className={`w-full px-6 py-4 rounded-xl transition-all duration-300 flex items-center justify-center gap-3 font-semibold text-lg ${darkMode
                            ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-700 disabled:to-gray-700 text-white'
                            : 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 disabled:from-gray-400 disabled:to-gray-400 text-white'
                        } shadow-lg`}
                >
                    {gettingLocation ? (
                        <>
                            <Loader2 className="w-6 h-6 animate-spin" />
                            <span>Detecting Location...</span>
                        </>
                    ) : (
                        <>
                            <Navigation className="w-6 h-6" />
                            <span>Use My Current Location</span>
                        </>
                    )}
                </motion.button>

                <div className="relative flex items-center gap-3">
                    <div className={`flex-1 h-px ${darkMode ? 'bg-white/20' : 'bg-gray-300'}`} />
                    <span className={`text-sm font-medium ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        OR
                    </span>
                    <div className={`flex-1 h-px ${darkMode ? 'bg-white/20' : 'bg-gray-300'}`} />
                </div>

                {/* City Search with Autocomplete */}
                <div className="relative">
                    <label
                        htmlFor="city"
                        className={`block text-sm font-semibold mb-2 transition-colors duration-300 flex items-center gap-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'
                            }`}
                    >
                        <Search className="w-4 h-4" />
                        Search City
                    </label>
                    <input
                        ref={inputRef}
                        type="text"
                        id="city"
                        value={cityQuery}
                        onChange={handleCityChange}
                        onKeyDown={handleKeyDown}
                        onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                        required
                        autoComplete="off"
                        className={`w-full px-4 py-3 rounded-xl border-2 focus:ring-4 focus:ring-purple-500/50 focus:border-purple-500 transition-all duration-300 ${darkMode
                                ? 'bg-white/10 border-white/20 text-white placeholder-gray-400'
                                : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                            }`}
                        placeholder="Type city name... (e.g., Mumbai, Delhi, New York)"
                    />

                    {/* Autocomplete Suggestions */}
                    <AnimatePresence>
                        {showSuggestions && suggestions.length > 0 && (
                            <motion.div
                                ref={suggestionsRef}
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className={`absolute z-50 w-full mt-2 rounded-xl shadow-2xl overflow-hidden border-2 ${darkMode
                                        ? 'bg-gray-800 border-white/20'
                                        : 'bg-white border-gray-200'
                                    }`}
                                style={{ maxHeight: '300px', overflowY: 'auto' }}
                            >
                                {suggestions.map((city, index) => (
                                    <motion.button
                                        key={`${city.name}-${city.country}`}
                                        type="button"
                                        onClick={() => selectCity(city)}
                                        whileHover={{ backgroundColor: darkMode ? 'rgba(139, 92, 246, 0.2)' : 'rgba(139, 92, 246, 0.1)' }}
                                        className={`w-full px-4 py-3 text-left transition-colors duration-200 flex items-center justify-between ${selectedIndex === index
                                                ? darkMode
                                                    ? 'bg-purple-600/30'
                                                    : 'bg-purple-100'
                                                : ''
                                            } ${darkMode
                                                ? 'hover:bg-purple-600/20 text-white'
                                                : 'hover:bg-purple-50 text-gray-900'
                                            }`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <MapPin className="w-4 h-4 text-purple-500" />
                                            <div>
                                                <div className="font-semibold">{city.name}</div>
                                                <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                                    {city.country}
                                                </div>
                                            </div>
                                        </div>
                                        <div className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                                            {city.lat.toFixed(2)}°, {city.lon.toFixed(2)}°
                                        </div>
                                    </motion.button>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {locationError && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mt-2 text-sm text-red-500 bg-red-50 border border-red-200 rounded-xl px-4 py-2 flex items-center gap-2"
                        >
                            <AlertCircle className="w-4 h-4" />
                            {locationError}
                        </motion.div>
                    )}

                    {formData.city && formData.lat && formData.lon && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className={`mt-2 text-sm px-4 py-2 rounded-lg flex items-center gap-2 ${darkMode ? 'bg-green-900/30 text-green-300' : 'bg-green-50 text-green-700'
                                }`}
                        >
                            <MapPin className="w-4 h-4" />
                            <span>
                                <strong>{formData.city}</strong> selected ({formData.lat.toFixed(4)}°, {formData.lon.toFixed(4)}°)
                            </span>
                        </motion.div>
                    )}
                </div>

                {/* Health Profile */}
                <div>
                    <label
                        htmlFor="profile"
                        className={`block text-sm font-semibold mb-2 transition-colors duration-300 flex items-center gap-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'
                            }`}
                    >
                        <User className="w-4 h-4" />
                        Health Profile (Optional)
                    </label>
                    <input
                        type="text"
                        id="profile"
                        name="profile"
                        value={formData.profile}
                        onChange={handleChange}
                        maxLength="200"
                        className={`w-full px-4 py-3 rounded-xl border-2 focus:ring-4 focus:ring-purple-500/50 focus:border-purple-500 transition-all duration-300 ${darkMode
                                ? 'bg-white/10 border-white/20 text-white placeholder-gray-400'
                                : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
                            }`}
                        placeholder="e.g., asthma, jogging, elderly"
                    />
                    <p
                        className={`text-xs mt-2 transition-colors duration-300 ${darkMode ? 'text-gray-400' : 'text-gray-500'
                            }`}
                    >
                        Add health conditions or activities for personalized advice
                    </p>
                </div>

                {/* Search Toggle */}
                <motion.div
                    whileHover={{ scale: 1.01 }}
                    className={`flex items-center gap-3 p-4 rounded-xl transition-all duration-300 cursor-pointer ${darkMode ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100'
                        }`}
                >
                    <input
                        type="checkbox"
                        id="useSearch"
                        name="useSearch"
                        checked={formData.useSearch}
                        onChange={handleChange}
                        className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500 focus:ring-2 cursor-pointer"
                    />
                    <label htmlFor="useSearch" className="flex-1 cursor-pointer">
                        <div className="flex items-center gap-2">
                            <Search className="w-4 h-4" />
                            <span
                                className={`text-sm font-semibold transition-colors duration-300 ${darkMode ? 'text-gray-200' : 'text-gray-800'
                                    }`}
                            >
                                Include latest weather news
                            </span>
                        </div>
                        <p
                            className={`text-xs mt-1 transition-colors duration-300 ${darkMode ? 'text-gray-400' : 'text-gray-600'
                                }`}
                        >
                            Search the web for current weather context and news
                        </p>
                    </label>
                </motion.div>

                {/* Submit Button */}
                <motion.button
                    whileHover={{ scale: loading ? 1 : 1.02 }}
                    whileTap={{ scale: loading ? 1 : 0.98 }}
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
                >
                    {loading ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Loading...</span>
                        </>
                    ) : (
                        <span>Get Forecast</span>
                    )}
                </motion.button>
            </form>

            {/* Error Message */}
            {error && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 bg-red-50 border-2 border-red-300 text-red-800 px-5 py-4 rounded-2xl shadow-lg"
                >
                    <div className="flex items-start gap-3">
                        <AlertCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                            <p className="font-bold text-lg mb-1">Unable to Get Forecast</p>
                            <p className="text-sm mb-3">{error}</p>
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={handleSubmit}
                                type="button"
                                className="bg-red-600 hover:bg-red-700 text-white font-semibold px-4 py-2 rounded-lg transition duration-200 text-sm"
                            >
                                🔄 Try Again
                            </motion.button>
                        </div>
                    </div>
                </motion.div>
            )}
        </motion.div>
    )
}

export default InputForm
