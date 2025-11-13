import { motion } from 'framer-motion'
import { Moon, Sun, CloudRain, Sparkles } from 'lucide-react'

function Header({ darkMode, setDarkMode, loading }) {
    return (
        <motion.header
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center relative"
        >
            {/* Dark Mode Toggle */}
            <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setDarkMode(!darkMode)}
                className={`absolute top-0 right-0 p-3 rounded-2xl transition-all duration-300 ${darkMode
                        ? 'bg-white/10 text-yellow-300 hover:bg-white/20'
                        : 'bg-purple-100 text-purple-700 hover:bg-purple-200'
                    } backdrop-blur-sm`}
            >
                <motion.div
                    initial={false}
                    animate={{ rotate: darkMode ? 0 : 180 }}
                    transition={{ duration: 0.5 }}
                >
                    {darkMode ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
                </motion.div>
            </motion.button>

            {/* Title with animated icon */}
            <div className="flex items-center justify-center gap-4 mb-4">
                <motion.div
                    animate={loading ? { rotate: 360 } : { y: [0, -10, 0] }}
                    transition={
                        loading
                            ? { duration: 2, repeat: Infinity, ease: "linear" }
                            : { duration: 2, repeat: Infinity, ease: "easeInOut" }
                    }
                    className="text-5xl sm:text-6xl"
                >
                    {loading ? '🌀' : '🌤️'}
                </motion.div>
            </div>

            <motion.h1
                className={`text-4xl sm:text-5xl md:text-6xl font-black mb-3 transition-colors duration-300 ${darkMode
                        ? 'text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400'
                        : 'text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600'
                    }`}
            >
                AgenticWeatherAI
            </motion.h1>

            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="space-y-2"
            >
                <p
                    className={`text-lg sm:text-xl font-medium transition-colors duration-300 ${darkMode ? 'text-gray-300' : 'text-gray-700'
                        }`}
                >
                    AI-Powered Weather & Air Quality Predictions
                </p>
                <div className="flex items-center justify-center gap-2 text-sm">
                    <Sparkles className={`w-4 h-4 ${darkMode ? 'text-purple-400' : 'text-purple-600'}`} />
                    <p
                        className={`transition-colors duration-300 ${darkMode ? 'text-gray-400' : 'text-gray-600'
                            }`}
                    >
                        Get personalized health advice for tomorrow's conditions
                    </p>
                </div>
            </motion.div>
        </motion.header>
    )
}

export default Header
