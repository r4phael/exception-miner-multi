/**
 * Catchs
 */
{
    //CHECK
    function badCatchExample() {
        try {
            const a = JSON.parse("value")
        } catch (error) {
            //useless catch
            /**
             * Somente relançar o erro
             */
            throw error
        }
    }
    
    //CHECK
    function badCatchExampleTwo() {
        try {
            const a = JSON.parse("value")
        } catch (error) {}
    }

    //CHECK
    function badCatchExamplethree() {
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
    function badThrowExample() {
        const a = Math.random()
        if(a > 0.5) {
            //no throw literal
            throw "error"
        }
    }
    
    //CHECK
    function badThrowExampleTwo() {
        const a = Math.random()
        if(a > 0.5) {
            throw ({ 'value': 'Error' })
        }
    }
    
    //CHECK
    function badThrowExampleThree() {
        const a = Math.random()
        if(a > 0.5) {
            throw Error("Error")
        }
    }

    //CHECK
    function genericThrowExample() {
        const a = Math.random()
        if(a > 0.5) {
            throw new Error("Error")
        }
    }
}