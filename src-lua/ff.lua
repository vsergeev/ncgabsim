local ff = {}

local FIELD_SIZE = 8
local ELEMENT_NUM = 2^FIELD_SIZE
local ELEMENT_MASK = ELEMENT_NUM-1
local PRIMITIVE_POLY = 0x1B
local GENERATOR = 0x03

local ff_exp_table = {}
local ff_log_table = {}
local ff_mul_table = {}
local ff_div_table = {}
local ff_sqrt_table = {}

local function elem_add(a, b)
    return bit.bxor(a, b)
end

local function elem_sub(a, b)
    return bit.bxor(a, b)
end

local function elem_mul(a, b)
    return ff_mul_table[a][b]
end

local function elem_div(a, b)
    return ff_div_table[a][b]
end

local function elem_sqrt(a)
    return ff_sqrt_table[a]
end

local function precompute()
    local ELEMENT_MSB_MASK = 2^(FIELD_SIZE-1)

    local function slow_elem_mul(a, b)
        local p = 0
        for i=1,FIELD_SIZE do
            if bit.band(b, 0x1) ~= 0 then
                p = bit.bxor(p, a)
            end
            if bit.band(a, ELEMENT_MSB_MASK) ~= 0 then
                a = bit.lshift(a, 1)
                a = bit.band(a, ELEMENT_MASK)
                a = bit.bxor(a, PRIMITIVE_POLY)
            else
                a = bit.lshift(a, 1)
                a = bit.band(a, ELEMENT_MASK)
            end
            b = bit.rshift(b, 1)
        end
        return p
    end

    -- Precompute exponent and logarithm tables
    ff_exp_table[0] = 0x01
    for i=1,ELEMENT_NUM-1 do
        ff_exp_table[i] = slow_elem_mul(ff_exp_table[i-1], GENERATOR)
        ff_log_table[ff_exp_table[i]] = i
    end

    -- Precompute multiplication table
    for a=0,ELEMENT_NUM-1 do
        ff_mul_table[a] = {}
        for b=0,ELEMENT_NUM-1 do
            if a == 0 or b == 0 then
                ff_mul_table[a][b] = 0
            else
                -- c = a * b = exp(log(a)) * exp(log(b)) = exp(log(a) + log(b))
                local c = ff_exp_table[(ff_log_table[a] + ff_log_table[b]) % ELEMENT_MASK]
                ff_mul_table[a][b] = c
            end
        end
    end

    -- Precompute division table
    for a=0,ELEMENT_NUM-1 do
        ff_div_table[a] = {}
        ff_div_table[a][0] = 1/0
        for b=1,ELEMENT_NUM-1 do
            -- c = a / b = a * (1/b) = a * exp(255 - log(b))
            local c = elem_mul(a, ff_exp_table[ELEMENT_MASK - ff_log_table[b]])
            ff_div_table[a][b] = c
        end
    end

    -- Precompute squareroot table
    for a=0,ELEMENT_NUM-1 do
        for b=0,ELEMENT_NUM-1 do
            if elem_mul(b, b) == a then
                ff_sqrt_table[a] = b
                break
            end
        end
    end
end

-- x <= x + y
local function row_add(x, y)
    assert(#x == #y, "x and y size mismatch")

    for i=1,#x do
        x[i] = elem_add(x[i], y[i])
    end

    return x
end

-- x <= x - y
local function row_sub(x, y)
    assert(#x == #y, "x and y size mismatch")

    for i=1,#x do
        x[i] = elem_sub(x[i], y[i])
    end

    return x
end

-- x * y
local function row_dot(x, y)
    assert(#x == #y, "x and y size mismatch")

    local result = 0

    for i=1,#x do
        result = elem_add(result, elem_mul(x[i], y[i]))
    end

    return result
end

-- x <= x * c
local function row_scalar_mul(x, c)
    for i=1,#x do
        x[i] = elem_mul(x[i], c)
    end

    return x
end

-- x <= x / c
local function row_scalar_div(x, c)
    for i=1,#x do
        x[i] = elem_div(x[i], c)
    end

    return x
end

local function rref(A, S)
    -- rref A

    -- A is an array of arrays representing matrix A, e.g.
    --  {
    --      {203, 213, 47, 198},
    --      {247, 221, 186, 19},
    --      {7, 185, 202, 45},
    --      {42, 141, 111, 209},
    --  }
    --
    -- S is an optional array representing the right-hand side of Ax=b, to be
    -- swapped as a A is row-reduced
    --  {219, 179, 133, 149}
    --

    if b then
        assert(#A == #b, "a and b size mismatch")
    end

    local pi = 1

    -- Iterate through each row
    for j=1,#A do
        -- While we do not have a pivot for this row
        while A[j][pi] == 0 do
            -- Find a row below to swap with for a pivot at pi
            for k=j+1,#A do
                if A[k][pi] ~= 0 then
                    -- Swap with j row
                    A[j], A[k] = A[k], A[j]
                    if S then
                        S[j], S[k] = S[k], S[j]
                    end
                    break
                end
            end

            -- Increment pivot index if we could not find a row to swap with
            if A[j][pi] == 0 then
                pi = pi + 1
            end

            -- If there are no pivots left, we're done reducing
            if pi == #A[1]+1 then
                return
            end
        end

        -- Divide through the row to have a pivot of 1
        -- A[j] = A[j] / A[j][pi]
        local pivot = A[j][pi]
        for i=1,#A[j] do
            A[j][i] = elem_div(A[j][i], pivot)
        end

        -- Eliminate above & below
        for k=1,#A do
            if k ~= j and A[k][pi] ~= 0 then
                -- A[k] = A[k] - A[j]*A[k][pi]
                local multiple = A[k][pi]
                for i=1,#A[k] do
                    A[k][i] = elem_sub(A[k][i], elem_mul(A[j][i], multiple))
                end
            end
        end

        -- Move onto the next pivot
        pi = pi + 1

        -- If there is no pivots left, we're done reducing
        if pi == #A[1]+1 then
            break
        end
    end
end

local function rref_solutions(A)
    local indices = {}

    for i=1,#A do
        local one_index = nil
        for j=1,#A[i] do
            if not one_index and A[i][j] == 1 then
                one_index = j
            elseif one_index and A[i][j] ~= 0 then
                one_index = nil
                break
            elseif A[i][j] ~= 0 then
                one_index = nil
                break
            end
        end

        if one_index then
            indices[#indices+1] = one_index
        end
    end

    return indices
end

precompute()

ff.elem_add = elem_add
ff.elem_sub = elem_sub
ff.elem_mul = elem_mul
ff.elem_div = elem_div
ff.elem_sqrt = elem_sqrt

ff.row_add = row_add
ff.row_sub = row_sub
ff.row_dot = row_dot
ff.row_scalar_mul = row_scalar_mul
ff.row_scalar_div = row_scalar_div

ff.rref = rref
ff.rref_solutions = rref_solutions

return ff
