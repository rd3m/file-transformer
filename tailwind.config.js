module.exports = {
	content: [
		"./core/templates/**/*.html", // Add your Django template files as content sources
	],
	theme: {
		extend: {},
	},
	variants: {
		extend: {},
	},
	daisyui: {
		themes: ["business"],
	},
	plugins: [require("daisyui")],
}
