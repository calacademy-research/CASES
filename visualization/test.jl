
using StatsPlots, DelimitedFiles, CSV, Plots, DataFrames
#using CSV,DelimitedFiles
# reading a delimited file
function loader()
    I = readdlm("US_exchanges_2018c.csv")
    return I
end

function joe()
    println("someone fetched joe")
    return 1
end


#println("Julia load complete")
#joe()