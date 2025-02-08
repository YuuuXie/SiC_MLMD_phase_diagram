from ovito.io import import_file, export_file

for P in [10, 30, 60, 90]:

    for T in [2800, 3200, 3400, 3600, 3800]:

        for trj in ["1equil", "2heathalf", "3coolhalf", "4nph"]:
            print(P, T, trj)
            pipeline = import_file(f"P{P}/T{T}/{trj}.bin")
            export_file(pipeline, f"P{P}_T{T}_{trj}.xyz", format="xyz", frame=-1, 
                columns = ["Particle Identifier", "Particle Type", "Position.X", "Position.Y", "Position.Z"])
