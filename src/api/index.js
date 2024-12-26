const express = require('express');
const brandsRoute = require('./brands');

const router = express.Router();

router.use('/brands', brandsRoute);

module.export = router;