local ff = require("ff")

describe("element operations", function ()
    it("checks add", function ()
        assert.are.equal(85, ff.elem_add(93, 8))
        assert.are.equal(100, ff.elem_add(141, 233))
        assert.are.equal(89, ff.elem_add(117, 44))
        assert.are.equal(142, ff.elem_add(226, 108))
        assert.are.equal(204, ff.elem_add(75, 135))
        assert.are.equal(75, ff.elem_add(75, 0))
        assert.are.equal(75, ff.elem_add(0, 75))
    end)

    it("checks sub", function ()
        assert.are.equal(85, ff.elem_sub(93, 8))
        assert.are.equal(100, ff.elem_sub(141, 233))
        assert.are.equal(89, ff.elem_sub(117, 44))
        assert.are.equal(142, ff.elem_sub(226, 108))
        assert.are.equal(204, ff.elem_sub(75, 135))
        assert.are.equal(75, ff.elem_sub(75, 0))
        assert.are.equal(75, ff.elem_sub(0, 75))
    end)

    it("checks mul", function ()
        assert.are.equal(222, ff.elem_mul(93, 8))
        assert.are.equal(249, ff.elem_mul(141, 233))
        assert.are.equal(104, ff.elem_mul(117, 44))
        assert.are.equal(21, ff.elem_mul(226, 108))
        assert.are.equal(80, ff.elem_mul(75, 135))
        assert.are.equal(0, ff.elem_mul(75, 0))
        assert.are.equal(0, ff.elem_mul(0, 75))
    end)

    it("checks div", function ()
        assert.are.equal(110, ff.elem_div(93, 8))
        assert.are.equal(39, ff.elem_div(141, 233))
        assert.are.equal(51, ff.elem_div(117, 44))
        assert.are.equal(192, ff.elem_div(226, 108))
        assert.are.equal(32, ff.elem_div(75, 135))
        assert.are.equal(1/0, ff.elem_div(75, 0))
        assert.are.equal(0, ff.elem_div(0, 75))
    end)

    it("checks sqrt", function ()
        assert.are.equal(224, ff.elem_sqrt(93))
        assert.are.equal(125, ff.elem_sqrt(141))
        assert.are.equal(202, ff.elem_sqrt(117))
        assert.are.equal(166, ff.elem_sqrt(226))
        assert.are.equal(28, ff.elem_sqrt(75))
        assert.are.equal(1, ff.elem_sqrt(1))
        assert.are.equal(0, ff.elem_sqrt(0))
    end)
end)

describe("row operations", function ()
    it("checks add", function ()
        local x = {120, 197, 86}
        local y = {255, 55, 130}

        assert.are.same({135, 242, 212}, ff.row_add(x, y))

        assert.has_error(function () ff.row_add({1,2}, {1,2,3}) end)
    end)

    it("checks sub", function ()
        local x = {120, 197, 86}
        local y = {255, 55, 130}

        assert.are.same({135, 242, 212}, ff.row_sub(x, y))

        assert.has_error(function () ff.row_sub({1,2}, {1,2,3}) end)
    end)

    it("checks dot", function ()
        local x = {120, 197, 86}
        local y = {255, 55, 130}

        assert.are.same(243, ff.row_dot(x, y))

        assert.has_error(function () ff.row_dot({1,2}, {1,2,3}) end)
    end)

    it("checks scalar mul", function ()
        local x = {120, 197, 86}
        assert.are.same({165, 60, 5}, ff.row_scalar_mul(x, 173))
    end)

    it("checks scalar div", function ()
        local x = {120, 197, 86}
        assert.are.same({144, 156, 29}, ff.row_scalar_div(x, 92))
    end)
end)

describe("matrix operations", function ()
    it("checks rref", function ()
        local A
        local S
        local indices

        ----------------------------------------
        -- Augmented matrices
        ----------------------------------------

        -- Invertible
        A = {
                {33, 247, 109, 71, 139, 1},
                {97, 221, 102, 127, 72, 2},
                {101, 126, 186, 90, 103, 3},
                {59, 234, 145, 197, 122, 4},
                {75, 9, 213, 9, 3, 5},
            }
        ff.rref(A)
        assert.are.same({{1, 0, 0, 0, 0, 192},
                         {0, 1, 0, 0, 0, 117},
                         {0, 0, 1, 0, 0, 37},
                         {0, 0, 0, 1, 0, 200},
                         {0, 0, 0, 0, 1, 142}}, A)

        -- Invertible
        A = {
                {89,234,225,241,246,123,48,212,102,85,147},
                {63,41,49,214,92,61,150,165,223,94,78},
                {237,45,39,103,225,172,12,154,203,200,147},
                {69,177,100,102,15,114,128,54,102,56,28},
                {37,234,224,17,142,62,26,155,94,246,24},
                {68,180,101,66,151,239,171,128,217,109,43},
                {211,139,77,137,188,128,24,153,182,172,217},
                {155,174,127,83,110,172,209,149,85,166,122},
                {89,179,160,10,198,54,185,50,180,119,16},
                {145,53,190,240,96,141,141,45,150,250,1},
            }
        ff.rref(A)
        assert.are.same({{1,0,0,0,0,0,0,0,0,0,182},
                         {0,1,0,0,0,0,0,0,0,0,107},
                         {0,0,1,0,0,0,0,0,0,0,144},
                         {0,0,0,1,0,0,0,0,0,0,221},
                         {0,0,0,0,1,0,0,0,0,0,156},
                         {0,0,0,0,0,1,0,0,0,0,136},
                         {0,0,0,0,0,0,1,0,0,0,217},
                         {0,0,0,0,0,0,0,1,0,0,9},
                         {0,0,0,0,0,0,0,0,1,0,193},
                         {0,0,0,0,0,0,0,0,0,1,90}}, A)


        -- Linearly dependent
        A = {
                {10,160,8,140},
                {82,64,59,166},
                {98,17,32,37},
                {196,34,64,74},
            }
        ff.rref(A)
        assert.are.same({{1,0,0,194},
                         {0,1,0,205},
                         {0,0,1,158},
                         {0,0,0,0}}, A)

        -- Low rank
        A = {
                {136,255,21},
                {230,29,96},
                {194,100,8},
                {232,19,229},
                {66,40,95},
            }
        ff.rref(A)
        assert.are.same({{1,0,0},
                         {0,1,0},
                         {0,0,1},
                         {0,0,0},
                         {0,0,0}}, A)

        -- Low rank
        A = {
                {0,227,137,140},
                {0,205,16,23},
                {0,162,177,29}
            }
        ff.rref(A)
        assert.are.same({{0,1,0,0},
                         {0,0,1,0},
                         {0,0,0,1}}, A)

        ----------------------------------------
        -- Non-augmented
        ----------------------------------------

        -- Zeros
        A = {
                {0,0,0},
                {0,0,0},
                {0,0,0}
            }
        S = {1,2,3}
        ff.rref(A)
        assert.are.same({{0,0,0},
                         {0,0,0},
                         {0,0,0}}, A)
        assert.are.same({1,2,3}, S)
        indices = ff.rref_solutions(A)
        assert.are.same({}, indices)

        -- Invertible
        A = {
                {33, 247, 109, 71, 139},
                {97, 221, 102, 127, 72},
                {101, 126, 186, 90, 103},
                {59, 234, 145, 197, 122},
                {75, 9, 213, 9, 3},
            }
        S = {1,2,3,4,5}
        ff.rref(A)
        assert.are.same({{1, 0, 0, 0, 0},
                         {0, 1, 0, 0, 0},
                         {0, 0, 1, 0, 0},
                         {0, 0, 0, 1, 0},
                         {0, 0, 0, 0, 1}}, A)
        assert.are.same({1,2,3,4,5}, S)
        indices = ff.rref_solutions(A)
        assert.are.same({1,2,3,4,5}, indices)

        -- Invertible with swapping
        A = {
                {0, 0, 0, 1, 0},
                {0, 1, 0, 0, 0},
                {0, 0, 1, 0, 0},
                {1, 0, 0, 0, 0},
                {0, 0, 0, 0, 1},
            }
        S = {1,2,3,4,5}
        ff.rref(A, S)
        assert.are.same({{1, 0, 0, 0, 0},
                         {0, 1, 0, 0, 0},
                         {0, 0, 1, 0, 0},
                         {0, 0, 0, 1, 0},
                         {0, 0, 0, 0, 1}}, A)
        assert.are.same({4,2,3,1,5}, S)
        indices = ff.rref_solutions(A)
        assert.are.same({1,2,3,4,5}, indices)

        -- Linearly dependent
        A = {
                {10,160,8},
                {82,64,59},
                {98,17,32},
                {196,34,64},
            }
        ff.rref(A)
        assert.are.same({{1,0,0},
                         {0,1,0},
                         {0,0,1},
                         {0,0,0}}, A)
        indices = ff.rref_solutions(A)
        assert.are.same({1,2,3}, indices)

        -- Low rank
        A = {
                {136,255},
                {230,29},
                {194,100},
                {232,19},
                {66,40},
            }
        ff.rref(A)
        assert.are.same({{1,0},
                         {0,1},
                         {0,0},
                         {0,0},
                         {0,0}}, A)
        indices = ff.rref_solutions(A)
        assert.are.same({1,2}, indices)

        -- Low rank
        A = {
                {0,227,137},
                {0,205,16},
                {0,162,177}
            }
        ff.rref(A)
        assert.are.same({{0,1,0},
                         {0,0,1},
                         {0,0,0}}, A)
        indices = ff.rref_solutions(A)
        assert.are.same({2,3}, indices)
    end)
end)
