## Objectives 

Understand probability distributions in financial markets

Explore descriptive statistics: mean, variance, skewness, kurtosis

Learn how randomness drives returns & portfolio risk

Do hands-on simulations: random walks, Monte Carlo, VaR

# Installing Typescript via npm
- TypeScript is JavaScript with syntax for types.

## Download nvm as dependencey manager and Nodejs as environment

```python
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# in lieu of restarting the shell
\. "$HOME/.nvm/nvm.sh"

# Download and install Node.js:
nvm install 22

# Verify the Node.js version:
node -v # Should print "v22.20.0".

# Verify npm version:
npm -v # Should print "10.9.3".

# New version of npm 
npm install -g npm@11.6.2
```
## Use npm to download typescript 

```python
npm install typescript --save-dev
```
## To start a dummy typescript folder 

```bash
# 1️⃣ Create a new project folder
mkdir ts-stock-dashboard
cd ts-stock-dashboard

# 2️⃣ Create a React + TypeScript app using Vite (fast, modern)
npm create vite@latest

# When prompted:
# ✔ Project name: ts-stock-dashboard
# ✔ Select a framework: › React
# ✔ Select a variant: › TypeScript

cd ts-stock-dashboard
npm install
npm run dev
npm install recharts tailwindcss postcss autoprefixer @tailwindcss/vite papaparse
```

## For Tailwindcss installation [follow this link](https://tailwindcss.com/docs/installation/framework-guides/react-router)

- Config the vite plugin - vite.config.ts
```
import tailwindcss from '@tailwindcss/vite' 
```
- Add tailwindcss in the css file 
```src/App.css
@import "tailwindcss";
```
- Start the Tailwind CLI build process
```bash
npx @tailwindcss/cli -i ./src/index.css -o ./src/output.css --watch
```
- start using tailwindcss with your html
```html
<link ref="./output.css" rel="stylesheet">
```


