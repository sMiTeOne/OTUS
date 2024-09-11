box.cfg{listen = 3301}

stations = box.schema.space.create('stations', { if_not_exists = true } )

box.space.stations:format({
    { 'code', type = 'string' },
    { 'name', type = 'string' }
})

box.space.stations:create_index('code', { parts = { 'code' }, if_not_exists = true } )
box.space.stations:create_index('name', { parts = { 'name' }, if_not_exists = true } )

box.schema.func.create('search', {
    body = [[
    function(name)
        return box.space.stations.index.name:select({ name }, { iterator = 'GE', limit = 3 })
    end
    ]],
    if_not_exists = true
})
