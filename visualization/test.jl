
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

function main(age_fracs)
    for i = 1:4
        for j = 1:4
           print("age_fracs[i][j],"   ")
        end
        print("\n")
    end
end


#println("Julia load complete")
#joe()

foo = 99
