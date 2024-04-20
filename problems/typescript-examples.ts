/**
 * Catchs
 */
{
    //CHECK
    function uselessCatch() {
        try {
            const a = JSON.parse("value")
        } catch (error) {
            //useless catch
            /**
             * only rethrow error
             */
            throw error
        }
    }
    
    //CHECK
    function ignoreError() {
        try {
            const a = JSON.parse("value")
        } catch (error) {}
    }

    //CHECK
    function reassignErrorObj() {
        try {
            const a = JSON.parse("value")
        } catch (error) {
            //antipattern: reassign error
            error = { 'value': 2 }
            console.error(error)
        }
    }
}

/**
 * Throw
 */

{
    //CHECK
    function throwLiteral() {
        const a = Math.random()
        if(a > 0.5) {
            //no throw literal
            throw "error"
        }
    }
    
    //CHECK
    function throwLiteral2() {
        const a = Math.random()
        if(a > 0.5) {
            throw ({ 'value': 'Error' })
        }
    }
    
    //CHECK
    function throwFunction() {
        const a = Math.random()
        if(a > 0.5) {
            //lose the error stack
            throw Error("Error")
        }
    }

    //CHECK
    function genericThrowExample() {
        const a = Math.random()
        if(a > 0.5) {
            //Generic error obj
            throw new Error("Error")
        }
    }
}