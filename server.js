const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const PORT = process.env.PORT || 3001;
const brandRoutes = require('./src/routes/brands')

app.use(bodyParser.json());
app.use(
    bodyParser.urlencoded({
        extended: true,
    })
);
app.use(express.json());

app.use('/api', brandRoutes);

app.listen(PORT, () => {
    console.log(`App listening at http://localhost:${PORT}`)
})