import baseAPI from './base'

export async function printAPI(action, parameter) {
    return await baseAPI(`print__${action}`, parameter)
}
